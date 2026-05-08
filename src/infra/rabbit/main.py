import logging
from contextlib import asynccontextmanager
from typing import Annotated

from faststream import Context, ContextRepo, ExceptionMiddleware, FastStream
from faststream.rabbit import Channel, RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DomainException
from src.core.response import ErrorResponse, ResponseMessage
from src.env_config import env
from src.infra.postgre.engine import DatabaseSessionManager
from src.infra.redis.engine import RedisSessionManager

from . import api

exc_middleware = ExceptionMiddleware()
logger = logging.getLogger(__name__)


@exc_middleware.add_handler(DomainException, publish=True)
async def error_handler(
    exc: DomainException,
    db_session: Annotated[AsyncSession | None, Context("db_session", default=None)] = None,
) -> ResponseMessage[ErrorResponse]:
    if db_session is not None:
        await db_session.rollback()
    return ResponseMessage(
        status=exc.status_code, message=ErrorResponse(message=exc.message)
    )


broker = RabbitBroker(
    env.rabbit.url,
    middlewares=[exc_middleware],
    default_channel=Channel(prefetch_count=10),
)

broker.include_router(api.router)


@asynccontextmanager
async def lifespan(context: ContextRepo):
    session_manager = DatabaseSessionManager(env.postgres.url)
    context.set_global("session_manager", session_manager)

    redis_engine = RedisSessionManager(env.redis.url)
    context.set_global("redis_engine", redis_engine)

    context.set_global("broker", broker)

    yield

    if await redis_engine.opened:
        await redis_engine.close()
    if await session_manager.opened:
        await session_manager.close()


app = FastStream(broker, lifespan=lifespan)
