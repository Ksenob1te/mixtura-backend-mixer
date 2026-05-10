from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundException
from src.core.interfaces.repo.match import MatchRepositoryProtocol
from src.core.models.match import Match, MatchCreate, MatchUpdate
from src.core.models.stage import StageFormat
from .base import BaseRepository
from ..models import BracketModel, EventModel, MatchModel, MatchScoreModel, MatchSlotModel, StageGroupModel, StageModel, TeamModel


class MatchRepository(BaseRepository[MatchModel, MatchCreate, Match, MatchUpdate], MatchRepositoryProtocol):
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
        return await self.get_list(
            offset, limit, None,
            MatchModel.group_id == group_id
        )

    async def next_match_index(self, group_id: UUID) -> int:
        stmt = select(func.max(MatchModel.match_index)).where(MatchModel.group_id == group_id)
        result = await self._session.scalar(stmt)
        return (result or 0) + 1

    async def list_active_team_ids_by_event(self, event_id: UUID) -> set[UUID]:
        stmt = (
            select(MatchScoreModel.team_id)
            .join(MatchSlotModel, MatchScoreModel.slot_id == MatchSlotModel.id)
            .join(MatchModel, MatchSlotModel.match_id == MatchModel.id)
            .join(StageGroupModel, MatchModel.group_id == StageGroupModel.id)
            .join(StageModel, StageGroupModel.stage_id == StageModel.id)
            .join(BracketModel, StageModel.bracket_id == BracketModel.id)
            .where(BracketModel.event_id == event_id)
            .where(MatchModel.time_end.is_(None))
        )
        result = await self._session.scalars(stmt)
        return set(result.all())

    async def list_active_draft_ids_by_event(self, event_id: UUID) -> set[UUID]:
        stmt = (
            select(TeamModel.draft_id)
            .join(MatchScoreModel, TeamModel.id == MatchScoreModel.team_id)
            .join(MatchSlotModel, MatchScoreModel.slot_id == MatchSlotModel.id)
            .join(MatchModel, MatchSlotModel.match_id == MatchModel.id)
            .join(StageGroupModel, MatchModel.group_id == StageGroupModel.id)
            .join(StageModel, StageGroupModel.stage_id == StageModel.id)
            .join(BracketModel, StageModel.bracket_id == BracketModel.id)
            .where(BracketModel.event_id == event_id)
            .where(MatchModel.time_end.is_(None))
            .where(TeamModel.draft_id.is_not(None))
        )
        result = await self._session.scalars(stmt)
        return {draft_id for draft_id in result.all() if draft_id is not None}

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

    async def get_event_context(self, match_id: UUID) -> tuple[UUID, UUID, StageFormat, UUID, UUID, UUID] | None:
        stmt = (
            select(
                BracketModel.event_id,
                EventModel.server_id,
                StageModel.format,
                BracketModel.id,
                StageModel.id,
                StageGroupModel.id,
            )
            .join(EventModel, BracketModel.event_id == EventModel.id)
            .join(StageModel, StageModel.bracket_id == BracketModel.id)
            .join(StageGroupModel, StageGroupModel.stage_id == StageModel.id)
            .join(MatchModel, MatchModel.group_id == StageGroupModel.id)
            .where(MatchModel.id == match_id)
        )
        row = (await self._session.execute(stmt)).first()
        if row is None:
            return None
        return row[0], row[1], row[2], row[3], row[4], row[5]

    async def list_by_event(
        self,
        event_id: UUID,
        offset: int = 0,
        limit: int = 100,
        active: bool | None = None,
    ) -> Sequence[Match]:
        stmt = (
            select(MatchModel)
            .join(StageGroupModel, MatchModel.group_id == StageGroupModel.id)
            .join(StageModel, StageGroupModel.stage_id == StageModel.id)
            .join(BracketModel, StageModel.bracket_id == BracketModel.id)
            .where(BracketModel.event_id == event_id)
            .options(selectinload(MatchModel.slots).selectinload(MatchSlotModel.score))
            .offset(offset)
            .limit(limit)
        )
        if active is True:
            stmt = stmt.where(MatchModel.time_end.is_(None))
        elif active is False:
            stmt = stmt.where(MatchModel.time_end.is_not(None))
        result = await self._session.scalars(stmt)
        return [self._to_dto(item) for item in result.all()]

    async def update(self, match_id: UUID, dto: MatchUpdate) -> Match:  # type: ignore[override]
        obj = await self._get_model(match_id)
        if not obj:
            raise NotFoundException("Match not found")
        update_data = self._dto_to_data(dto, exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self._flush()
        await self._session.refresh(obj)
        return self._to_dto(obj)
