from faststream import Context, Depends

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

import logging


logger = logging.getLogger(__name__)


async def get_db_session(session_manager: Annotated[DatabaseSessionManager, Context()]):
    async with session_manager.session() as session:
        yield session


async def get_redis_session(redis_engine: Annotated[RedisSessionManager, Context()]):
    async with redis_engine.client() as redis:
        yield redis


async def get_redis_repository(redis: Annotated[Redis, Depends(get_redis_session)]):
    return RedisRepository(redis)



