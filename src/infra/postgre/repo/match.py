from uuid import UUID
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models import MatchModel, MatchSlotModel, StageGroupModel, StageModel, BracketModel
from .base import BaseRepository
from src.core.models.match import Match

from src.core.interfaces.repo.match import MatchRepositoryProtocol


class MatchRepository(MatchRepositoryProtocol, BaseRepository[MatchModel, Match]):
    model = MatchModel
    dto_model = Match

    async def get(
            self,
            field_id: UUID,
            load_slots: bool = False,
            load_group: bool = False
    ) -> Match | None:
        options = []
        if load_slots:
            options.append(selectinload(MatchModel.slots).selectinload(MatchSlotModel.score))
        if load_group:
            options.append(selectinload(MatchModel.group))

        return await self._get(field_id, options=options)

    async def list_by_stage_group(self, group_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Match]:
        return await self.list(
            offset, limit, None,
            MatchModel.group_id == group_id
        )

    async def count_incomplete_matches_by_event(self, event_id: UUID) -> int:
        stmt = (
            select(func.count(MatchModel.id))
            .join(StageGroupModel, MatchModel.group_id == StageGroupModel.id)
            .join(StageModel, StageGroupModel.stage_id == StageModel.id)
            .join(BracketModel, StageModel.bracket_id == BracketModel.id)
            .where(BracketModel.event_id == event_id)
            .where(MatchModel.time_end.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
