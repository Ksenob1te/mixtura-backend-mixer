from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import MatchSlotModel
from .base import BaseRepository


class MatchSlotRepository(BaseRepository[MatchSlotModel]):
    model = MatchSlotModel

    async def get(
            self,
            field_id: UUID,
            load_score: bool = False
    ) -> MatchSlotModel | None:
        options = []
        if load_score:
            options.append(selectinload(MatchSlotModel.score))

        return await super()._get(field_id, options=options)

    async def list_by_match(self, match_id: UUID) -> Sequence[MatchSlotModel]:
        # Custom query because of order_by
        stmt = select(MatchSlotModel).where(MatchSlotModel.match_id == match_id).order_by(MatchSlotModel.slot_num)
        result = await self._session.scalars(stmt)
        return result.all()
