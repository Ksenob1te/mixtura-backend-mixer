import logging
from contextlib import asynccontextmanager

from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.rabbit import Channel, RabbitBroker

from src.core.exceptions import DomainException
from src.core.response import ErrorResponse, ResponseMessage
from src.env_config import env
from src.infra.postgre.engine import DatabaseSessionManager

from . import api

exc_middleware = ExceptionMiddleware()
logger = logging.getLogger(__name__)


@exc_middleware.add_handler(DomainException, publish=True)
async def error_handler(
    exc: DomainException,
) -> ResponseMessage[ErrorResponse]:
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
    yield
    if await session_manager.opened:
        await session_manager.close()


app = FastStream(broker, lifespan=lifespan)
