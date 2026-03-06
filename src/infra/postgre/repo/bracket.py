from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Bracket
from .base import BaseRepository


class BracketRepository(BaseRepository[Bracket]):
    model = Bracket

    async def get(
            self,
            field_id: UUID,
            load_placements: bool = False,
            load_stages: bool = False
    ) -> Bracket | None:
        options = []
        if load_placements:
            options.append(selectinload(Bracket.placements))
        if load_stages:
            options.append(selectinload(Bracket.stages))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Bracket]:
        return await self.list(
            offset, limit, None,
            Bracket.event_id == event_id
        )
