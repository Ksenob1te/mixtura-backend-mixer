from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.draft import DraftRepositoryProtocol
from src.core.models.draft import Draft, DraftCreate, DraftUpdate
from .base import BaseRepository
from ..models import DraftModel


class DraftRepository(BaseRepository[DraftModel, DraftCreate, Draft, DraftUpdate], DraftRepositoryProtocol):
    model = DraftModel
    dto_model = Draft

    async def get(
            self,
            field_id: UUID,
            load_drafted_players: bool = False
    ) -> Draft | None:
        options = []
        if load_drafted_players:
            options.append(selectinload(DraftModel.drafted_players))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Draft]:
        return await self.list(
            offset, limit, None,
            DraftModel.event_id == event_id
        )
