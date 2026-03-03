from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import Stage
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class StageRepository(BaseRepository):
    async def get_by_id(
            self,
            stage_id: UUID,
            load_groups: bool = False,
            load_settings: bool = False
    ) -> Stage | None:
        options = []
        if load_groups:
            options.append(selectinload(Stage.groups))
        if load_settings:
            options.extend([
                selectinload(Stage.round_robin_settings),
                selectinload(Stage.swiss_settings)
            ])

        return await self._session.get(Stage, stage_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Stage]:
        stmt = (
            select(Stage)
            .where(Stage.bracket_id == bracket_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, stage: Stage) -> Stage:
        self._session.add(stage)
        await self._flush()
        await self._session.refresh(stage)
        return stage

    async def update(self, stage: Stage) -> Stage:
        stage = await self._session.merge(stage)
        await self._flush()
        return stage

    async def delete(self, stage_id: UUID) -> None:
        stage = await self.get_by_id(stage_id)
        if stage:
            await self._session.delete(stage)
            await self._flush()
