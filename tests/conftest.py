import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from testcontainers.postgres import PostgresContainer

from src.infra.postgre.engine import Base


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def postgres_container() -> AsyncGenerator[str, None]:
    with PostgresContainer("postgres:16-alpine") as container:
        container.start()
        sync_url = container.get_connection_url()
        async_url = sync_url.replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        ).replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        yield async_url


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_engine(postgres_container: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        postgres_container,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with async_engine.connect() as conn:
        trans = await conn.begin()

        session_factory = async_sessionmaker(
            conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"
        )

        async with session_factory() as session:
            yield session

        await trans.rollback()
