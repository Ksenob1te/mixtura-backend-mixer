from uuid import UUID
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..models import RoundRobinSettings
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class RoundRobinSettingsRepository(BaseRepository):
    async def get_by_stage_id(
            self,
            stage_id: UUID,
            load_stage: bool = False
    ) -> RoundRobinSettings | None:
        stmt = select(RoundRobinSettings).where(RoundRobinSettings.stage_id == stage_id)

        if load_stage:
            stmt = stmt.options(selectinload(RoundRobinSettings.stage))

        return await self._session.scalar(stmt)

    async def create(self, settings: RoundRobinSettings) -> RoundRobinSettings:
        self._session.add(settings)
        await self._flush()
        await self._session.refresh(settings)
        return settings

    async def update(self, settings: RoundRobinSettings) -> RoundRobinSettings:
        settings = await self._session.merge(settings)
        await self._flush()
        return settings

    async def delete_by_stage(self, stage_id: UUID) -> None:
        settings = await self.get_by_stage_id(stage_id)
        if settings:
            await self._session.delete(settings)
            await self._flush()
