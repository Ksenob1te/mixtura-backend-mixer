import asyncio
import json
import logging
import os
import socket
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aio_pika
import aio_pika.abc

from src.core.exceptions import (
    RpcClientClosedError,
    RpcOverloadedError,
    RpcPublishError,
    RpcTimeoutError,
)

logger = logging.getLogger(__name__)

_DEFAULT_MAX_PENDING = 256


def _make_reply_queue_name() -> str:
    hostname = socket.gethostname()
    pid = os.getpid()
    unique = uuid.uuid4().hex[:8]
    return f"mixer.{hostname}.{pid}.{unique}.replies"


@dataclass(frozen=True)
class RpcResponse:
    body: bytes
    correlation_id: str
    headers: Mapping[str, Any]
    content_type: str | None = None


class RabbitRpcClient:
    def __init__(
        self,
        amqp_url: str,
        *,
        max_pending: int = _DEFAULT_MAX_PENDING,
        default_timeout: float | None = None,
    ) -> None:
        self._amqp_url = amqp_url
        self._max_pending = max_pending
        self._default_timeout = default_timeout or 30.0

        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._reply_queue: aio_pika.abc.AbstractQueue | None = None
        self._reply_queue_name: str = _make_reply_queue_name()

        self._pending: dict[str, asyncio.Future[RpcResponse]] = {}
        self._semaphore = asyncio.Semaphore(max_pending)
        self._started = False
        self._consume_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._started:
            return

        logger.info("Opening RabbitRpcClient connection to %s", self._amqp_url)
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._max_pending)

        self._reply_queue = await self._channel.declare_queue(
            self._reply_queue_name,
            exclusive=True,
            auto_delete=True,
            durable=False,
        )

        self._started = True
        self._consume_task = asyncio.create_task(self._consume_replies())
        logger.info(
            "RabbitRpcClient started, reply queue=%s, max_pending=%d",
            self._reply_queue_name,
            self._max_pending,
        )

    async def stop(self) -> None:
        if not self._started:
            return

        self._started = False

        if self._consume_task is not None:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
            self._consume_task = None

        for future in self._pending.values():
            if not future.done():
                future.set_exception(RpcClientClosedError())
        self._pending.clear()

        if self._connection and not self._connection.is_closed:
            await self._connection.close()

        logger.info("RabbitRpcClient stopped")

    async def request(
        self,
        queue: str,
        payload: Any,
        *,
        timeout: float | None = None,
        headers: dict[str, Any] | None = None,
    ) -> RpcResponse:
        if not self._started:
            raise RpcClientClosedError()

        effective_timeout = timeout if timeout is not None else self._default_timeout

        acquired = self._semaphore.locked()
        if acquired:
            raise RpcOverloadedError()

        async with self._semaphore:
            return await self._do_request(
                queue=queue,
                payload=payload,
                timeout=effective_timeout,
                headers=headers,
            )

    async def _do_request(
        self,
        queue: str,
        payload: Any,
        *,
        timeout: float,
        headers: dict[str, Any] | None,
    ) -> RpcResponse:
        correlation_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future: asyncio.Future[RpcResponse] = loop.create_future()

        self._pending[correlation_id] = future

        timeout_ms = int(timeout * 1000)

        body = self._serialize_payload(payload)

        message_headers: dict[str, Any] = {
            "x-correlation-id": correlation_id,
            "x-timeout-ms": timeout_ms,
        }
        if headers:
            message_headers.update(headers)

        message = aio_pika.Message(
            body=body,
            correlation_id=correlation_id,
            reply_to=self._reply_queue_name,
            content_type="application/json",
            expiration=timeout_ms,
            headers=message_headers,
        )

        try:
            if self._channel is None:
                raise RpcPublishError("Channel is not available")

            await self._channel.default_exchange.publish(
                message,
                routing_key=queue,
            )
        except RpcPublishError:
            raise
        except Exception:
            self._pending.pop(correlation_id, None)
            logger.exception("Failed to publish RPC request to queue '%s'", queue)
            raise RpcPublishError()

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(correlation_id, None)
            logger.warning(
                "RPC call to queue '%s' timed out after %.1fs", queue, timeout
            )
            raise RpcTimeoutError()
        except RpcClientClosedError:
            raise
        except Exception:
            self._pending.pop(correlation_id, None)
            raise

    async def _consume_replies(self) -> None:
        if self._reply_queue is None:
            return

        async with self._reply_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._handle_reply(message)

    async def _handle_reply(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        correlation_id = message.correlation_id or ""

        future = self._pending.pop(correlation_id, None)
        if future is None:
            logger.debug(
                "Late or duplicate reply for correlation_id=%s, ignoring",
                correlation_id,
            )
            return

        if future.done():
            logger.debug(
                "Future already done for correlation_id=%s, ignoring reply",
                correlation_id,
            )
            return

        response = RpcResponse(
            body=message.body,
            correlation_id=correlation_id,
            headers=message.headers or {},
            content_type=message.content_type,
        )

        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(future.set_result, response)

    @staticmethod
    def _serialize_payload(payload: Any) -> bytes:
        if payload is None:
            return b"null"
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        if hasattr(payload, "model_dump"):
            return json.dumps(payload.model_dump(mode="json", exclude_none=True)).encode("utf-8")
        if hasattr(payload, "dict"):
            return json.dumps(payload.dict()).encode("utf-8")
        return json.dumps(payload).encode("utf-8")
