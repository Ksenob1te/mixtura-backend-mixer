from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import Match, MatchSlot, MatchScore
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class MatchRepository(BaseRepository):
    async def get_by_id(
            self,
            match_id: UUID,
            load_slots: bool = False,
            load_group: bool = False
    ) -> Match | None:
        options = []
        if load_slots:
            options.append(selectinload(Match.slots).selectinload(MatchSlot.score))
        if load_group:
            options.append(selectinload(Match.group))

        return await self._session.get(Match, match_id, options=options)

    async def list_by_stage_group(self, group_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Match]:
        stmt = (
            select(Match)
            .where(Match.group_id == group_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, match: Match) -> Match:
        self._session.add(match)
        await self._flush()
        await self._session.refresh(match)
        return match

    async def update(self, match: Match) -> Match:
        match = await self._session.merge(match)
        await self._flush()
        return match

    async def delete(self, match_id: UUID) -> None:
        match = await self.get_by_id(match_id)
        if match:
            await self._session.delete(match)
            await self._flush()
