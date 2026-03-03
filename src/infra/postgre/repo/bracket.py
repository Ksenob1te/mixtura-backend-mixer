from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import Bracket, BracketPlacement
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class BracketRepository(BaseRepository):
    async def get_by_id(
            self,
            bracket_id: UUID,
            load_placements: bool = False,
            load_stages: bool = False
    ) -> Bracket | None:
        options = []
        if load_placements:
            options.append(selectinload(Bracket.placements))
        if load_stages:
            options.append(selectinload(Bracket.stages))

        return await self._session.get(Bracket, bracket_id, options=options)

    async def list_by_event(self, event_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Bracket]:
        stmt = (
            select(Bracket)
            .where(Bracket.event_id == event_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, bracket: Bracket) -> Bracket:
        self._session.add(bracket)
        await self._flush()
        await self._session.refresh(bracket)
        return bracket

    async def update(self, bracket: Bracket) -> Bracket:
        bracket = await self._session.merge(bracket)
        await self._flush()
        return bracket

    async def delete(self, bracket_id: UUID) -> None:
        bracket = await self.get_by_id(bracket_id)
        if bracket:
            await self._session.delete(bracket)
            await self._flush()
