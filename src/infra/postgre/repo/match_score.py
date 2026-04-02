from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..models import MatchScoreModel
from .base import BaseRepository


class MatchScoreRepository(BaseRepository[MatchScoreModel]):
    model = MatchScoreModel

    async def get(
            self,
            field_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScoreModel | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScoreModel.slot))
        if load_team:
            options.append(selectinload(MatchScoreModel.team))

        return await super()._get(field_id, options=options)

    async def get_by_slot_id(
            self,
            slot_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScoreModel | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScoreModel.slot))
        if load_team:
            options.append(selectinload(MatchScoreModel.team))

        stmt = select(MatchScoreModel).where(MatchScoreModel.slot_id == slot_id)
        if options:
            stmt = stmt.options(*options)

        return await self._session.scalar(stmt)
