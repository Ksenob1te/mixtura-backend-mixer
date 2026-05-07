from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.match_score import MatchScoreRepositoryProtocol
from src.core.models.match_score import MatchScore, MatchScoreCreate, MatchScoreUpdate
from .base import BaseRepository
from ..models import MatchScoreModel


class MatchScoreRepository(MatchScoreRepositoryProtocol, BaseRepository[MatchScoreModel, MatchScoreCreate, MatchScore, MatchScoreUpdate]):
    model = MatchScoreModel
    dto_model = MatchScore

    async def get(
            self,
            field_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScoreModel.slot))
        if load_team:
            options.append(selectinload(MatchScoreModel.team))

        return await self._get(field_id, options=options)

    async def get_by_slot_id(
            self,
            slot_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScoreModel.slot))
        if load_team:
            options.append(selectinload(MatchScoreModel.team))

        stmt = select(MatchScoreModel).where(MatchScoreModel.slot_id == slot_id)
        if options:
            stmt = stmt.options(*options)

        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None
