from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import BracketModel
from .base import BaseRepository


class BracketRepository(BaseRepository[BracketModel]):
    model = BracketModel

    async def get(
            self,
            field_id: UUID,
            load_placements: bool = False,
            load_stages: bool = False
    ) -> BracketModel | None:
        options = []
        if load_placements:
            options.append(selectinload(BracketModel.placements))
        if load_stages:
            options.append(selectinload(BracketModel.stages))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[BracketModel]:
        return await self.list(
            offset, limit, None,
            BracketModel.event_id == event_id
        )
