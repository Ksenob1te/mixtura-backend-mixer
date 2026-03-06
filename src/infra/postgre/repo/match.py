from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Match, MatchSlot
from .base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    model = Match

    async def get(
            self,
            field_id: UUID,
            load_slots: bool = False,
            load_group: bool = False
    ) -> Match | None:
        options = []
        if load_slots:
            options.append(selectinload(Match.slots).selectinload(MatchSlot.score))
        if load_group:
            options.append(selectinload(Match.group))

        return await super()._get(field_id, options=options)

    async def list_by_stage_group(self, group_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Match]:
        return await self.list(
            offset, limit, None,
            Match.group_id == group_id
        )
