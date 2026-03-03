from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Organizer
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class OrganizerRepository(BaseRepository):
    async def get_by_id(
            self,
            organizer_id: UUID,
            load_event: bool = False
    ) -> Organizer | None:
        options = []
        if load_event:
            options.append(selectinload(Organizer.event))

        return await self._session.get(Organizer, organizer_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[Organizer]:
        stmt = select(Organizer).where(Organizer.event_id == event_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, organizer: Organizer) -> Organizer:
        self._session.add(organizer)
        await self._flush()
        await self._session.refresh(organizer)
        return organizer

    async def update(self, organizer: Organizer) -> Organizer:
        organizer = await self._session.merge(organizer)
        await self._flush()
        return organizer

    async def delete(self, organizer_id: UUID) -> None:
        organizer = await self.get_by_id(organizer_id)
        if organizer:
            await self._session.delete(organizer)
            await self._flush()
