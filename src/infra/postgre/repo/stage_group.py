from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import StageGroup
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class StageGroupRepository(BaseRepository):
    async def get_by_id(
            self,
            group_id: UUID,
            load_matches: bool = False
    ) -> StageGroup | None:
        options = []
        if load_matches:
            options.append(selectinload(StageGroup.matches))

        return await self._session.get(StageGroup, group_id, options=options)

    async def list_by_stage(self, stage_id: UUID) -> Sequence[StageGroup]:
        stmt = select(StageGroup).where(StageGroup.stage_id == stage_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, group: StageGroup) -> StageGroup:
        self._session.add(group)
        await self._flush()
        await self._session.refresh(group)
        return group

    async def update(self, group: StageGroup) -> StageGroup:
        group = await self._session.merge(group)
        await self._flush()
        return group

    async def delete(self, group_id: UUID) -> None:
        group = await self.get_by_id(group_id)
        if group:
            await self._session.delete(group)
            await self._flush()
