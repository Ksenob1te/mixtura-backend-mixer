from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import ApplicationCustomField
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class ApplicationCustomFieldRepository(BaseRepository):
    async def get_by_id(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> ApplicationCustomField | None:
        options = []
        if load_event:
            options.append(selectinload(ApplicationCustomField.event))

        return await self._session.get(ApplicationCustomField, field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[ApplicationCustomField]:
        stmt = select(ApplicationCustomField).where(ApplicationCustomField.event_id == event_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, field: ApplicationCustomField) -> ApplicationCustomField:
        self._session.add(field)
        await self._flush()
        await self._session.refresh(field)
        return field

    async def update(self, field: ApplicationCustomField) -> ApplicationCustomField:
        field = await self._session.merge(field)
        await self._flush()
        return field

    async def delete(self, field_id: UUID) -> None:
        field = await self.get_by_id(field_id)
        if field:
            await self._session.delete(field)
            await self._flush()
