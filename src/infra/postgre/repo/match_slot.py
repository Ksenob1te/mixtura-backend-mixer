from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import MatchSlot
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class MatchSlotRepository(BaseRepository):
    async def get_by_id(
            self,
            slot_id: UUID,
            load_score: bool = False
    ) -> MatchSlot | None:
        options = []
        if load_score:
            options.append(selectinload(MatchSlot.score))

        return await self._session.get(MatchSlot, slot_id, options=options)

    async def list_by_match(self, match_id: UUID) -> Sequence[MatchSlot]:
        stmt = select(MatchSlot).where(MatchSlot.match_id == match_id).order_by(MatchSlot.slot_num)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, slot: MatchSlot) -> MatchSlot:
        self._session.add(slot)
        await self._flush()
        await self._session.refresh(slot)
        return slot

    async def update(self, slot: MatchSlot) -> MatchSlot:
        slot = await self._session.merge(slot)
        await self._flush()
        return slot

    async def delete(self, slot_id: UUID) -> None:
        slot = await self.get_by_id(slot_id)
        if slot:
            await self._session.delete(slot)
            await self._flush()
