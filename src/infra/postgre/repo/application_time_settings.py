from uuid import UUID
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..models import ApplicationTimeSettings
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class ApplicationTimeSettingsRepository(BaseRepository):
    async def get_by_event_id(
            self,
            event_id: UUID,
            load_event: bool = False
    ) -> ApplicationTimeSettings | None:
        stmt = select(ApplicationTimeSettings).where(ApplicationTimeSettings.event_id == event_id)

        if load_event:
            stmt = stmt.options(selectinload(ApplicationTimeSettings.event))

        return await self._session.scalar(stmt)

    async def create(self, settings: ApplicationTimeSettings) -> ApplicationTimeSettings:
        self._session.add(settings)
        await self._flush()
        await self._session.refresh(settings)
        return settings

    async def update(self, settings: ApplicationTimeSettings) -> ApplicationTimeSettings:
        settings = await self._session.merge(settings)
        await self._flush()
        return settings

    async def delete(self, event_id: UUID) -> None:
        settings = await self.get_by_event_id(event_id)
        if settings:
            await self._session.delete(settings)
            await self._flush()
