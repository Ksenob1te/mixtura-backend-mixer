from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..models import MatchScore
from .base import BaseRepository


class MatchScoreRepository(BaseRepository[MatchScore]):
    model = MatchScore

    async def get(
            self,
            field_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScore.slot))
        if load_team:
            options.append(selectinload(MatchScore.team))

        return await super()._get(field_id, options=options)

    async def get_by_slot_id(
            self,
            slot_id: UUID,
            load_slot: bool = False,
            load_team: bool = False
    ) -> MatchScore | None:
        options = []
        if load_slot:
            options.append(selectinload(MatchScore.slot))
        if load_team:
            options.append(selectinload(MatchScore.team))

        stmt = select(MatchScore).where(MatchScore.slot_id == slot_id)
        if options:
            stmt = stmt.options(*options)

        return await self._session.scalar(stmt)
