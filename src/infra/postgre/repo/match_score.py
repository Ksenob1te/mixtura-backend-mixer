from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..models import MatchScoreModel
from .base import BaseRepository
from src.core.models.match_score import MatchScore

from src.core.interfaces.repo.match_score import MatchScoreRepositoryProtocol


class MatchScoreRepository(MatchScoreRepositoryProtocol, BaseRepository[MatchScoreModel, MatchScore]):
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
