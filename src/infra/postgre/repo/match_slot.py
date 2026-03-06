from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import MatchSlot
from .base import BaseRepository


class MatchSlotRepository(BaseRepository[MatchSlot]):
    model = MatchSlot

    async def get(
            self,
            field_id: UUID,
            load_score: bool = False
    ) -> MatchSlot | None:
        options = []
        if load_score:
            options.append(selectinload(MatchSlot.score))

        return await super()._get(field_id, options=options)

    async def list_by_match(self, match_id: UUID) -> Sequence[MatchSlot]:
        # Custom query because of order_by
        stmt = select(MatchSlot).where(MatchSlot.match_id == match_id).order_by(MatchSlot.slot_num)
        result = await self._session.scalars(stmt)
        return result.all()
