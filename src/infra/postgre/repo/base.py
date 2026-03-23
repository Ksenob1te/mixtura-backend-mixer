from typing import Generic, TypeVar, Any, Sequence, Type, Protocol
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from ..engine import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self._session = session
        if not hasattr(self, "model"):
            # This allows repositories to define model as a class attribute
            # But falls back to dynamic resolution or requires setting it if logic depends on it
            raise NotImplementedError("Repository must define 'model' class attribute")

    async def _flush(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as exc:
            sql_state = getattr(exc.orig, "sqlstate", None)
            if sql_state == "23503":
                raise IntegrityForeignException() from exc
            if sql_state == "23505":
                raise IntegrityUniqueException() from exc
            raise IntegrityUnknownException() from exc

    async def _get(self, field_id: UUID, options: list[Any] | None = None) -> ModelType | None:
        stmt = select(self.model).where(getattr(self.model, "id") == field_id)
        if options:
            stmt = stmt.options(*options)
        result = await self._session.scalar(stmt)
        return result

    async def get(self, field_id: UUID) -> ModelType | None:
        return await self._get(field_id)

    async def list(
            self,
            offset: int = 0,
            limit: int | None = 100,
            options: list[Any] | None = None,
            *where_clauses
    ) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        if where_clauses:
            for clause in where_clauses:
                stmt = stmt.where(clause)
        if options:
            stmt = stmt.options(*options)

        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, obj: ModelType) -> ModelType:
        self._session.add(obj)
        await self._flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        if obj not in self._session:
            obj = await self._session.merge(obj)
        await self._flush()
        return obj

    async def delete(self, field_id: UUID) -> bool:
        obj = await self._get(field_id)
        if obj:
            await self._session.delete(obj)
            await self._flush()
            return True
        return False

    async def exists(self, field_id: UUID) -> bool:
        stmt = select(func.count()).select_from(self.model).where(getattr(self.model, "id") == field_id)
        count = await self._session.scalar(stmt)
        return (count or 0) > 0

    async def count(self, *where_clauses) -> int:
        stmt = select(func.count()).select_from(self.model)
        if where_clauses:
            for clause in where_clauses:
                stmt = stmt.where(clause)
        val = await self._session.scalar(stmt)
        return val or 0
