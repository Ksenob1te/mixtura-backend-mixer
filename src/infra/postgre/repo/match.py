from uuid import UUID
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models import Match, MatchSlot, StageGroup, Stage, Bracket
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

    async def count_incomplete_matches_by_event(self, event_id: UUID) -> int:
        """Return the number of matches in the event that have not ended."""
        stmt = (
            select(func.count(Match.id))
            .join(StageGroup, Match.group_id == StageGroup.id)
            .join(Stage, StageGroup.stage_id == Stage.id)
            .join(Bracket, Stage.bracket_id == Bracket.id)
            .where(Bracket.event_id == event_id)
            .where(Match.time_end.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
