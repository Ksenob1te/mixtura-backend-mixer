from uuid import UUID
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..models import MatchScore
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class MatchScoreRepository(BaseRepository):
    async def get_by_id(
            self,
            score_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScore.slot))
        if load_team:
            options.append(selectinload(MatchScore.team))

        return await self._session.get(MatchScore, score_id, options=options)

    async def get_by_slot_id(
            self,
            slot_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        stmt = select(MatchScore).where(MatchScore.slot_id == slot_id)

        if load_slot:
            stmt = stmt.options(selectinload(MatchScore.slot))
        if load_team:
            stmt = stmt.options(selectinload(MatchScore.team))

        return await self._session.scalar(stmt)

    async def create(self, score: MatchScore) -> MatchScore:
        self._session.add(score)
        await self._flush()
        await self._session.refresh(score)
        return score

    async def update(self, score: MatchScore) -> MatchScore:
        score = await self._session.merge(score)
        await self._flush()
        return score

    async def delete(self, score_id: UUID) -> None:
        score = await self.get_by_id(score_id)
        if score:
            await self._session.delete(score)
            await self._flush()
