from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.match_slot import MatchSlotRepositoryProtocol
from src.core.models.match_slot import MatchSlot, MatchSlotCreate
from .base import BaseRepository
from ..models import MatchSlotModel


class MatchSlotRepository(MatchSlotRepositoryProtocol, BaseRepository[MatchSlotModel, MatchSlotCreate, MatchSlot, MatchSlotCreate]):
    model = MatchSlotModel
    dto_model = MatchSlot

    async def get(
            self,
            field_id: UUID,
            load_score: bool = False
    ) -> MatchSlot | None:
        options = []
        if load_score:
            options.append(selectinload(MatchSlotModel.score))

        return await self._get(field_id, options=options)

    async def list_by_match(self, match_id: UUID) -> Sequence[MatchSlot]:
        # Custom query because of order_by
        stmt = select(MatchSlotModel).where(MatchSlotModel.match_id == match_id).order_by(MatchSlotModel.slot_num)
        result = await self._session.scalars(stmt)
        return [self._to_dto(item) for item in result.all()]
