from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.bracket import BracketRepositoryProtocol
from src.core.models.bracket import Bracket
from .base import BaseRepository
from ..models import BracketModel


class BracketRepository(BracketRepositoryProtocol, BaseRepository[BracketModel, Bracket]):
    model = BracketModel
    dto_model = Bracket

    async def get(
            self,
            field_id: UUID,
            load_placements: bool = False,
            load_stages: bool = False
    ) -> Bracket | None:
        options = []
        if load_placements:
            options.append(selectinload(BracketModel.placements))
        if load_stages:
            options.append(selectinload(BracketModel.stages))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Bracket]:
        return await self.list(
            offset, limit, None,
            BracketModel.event_id == event_id
        )
