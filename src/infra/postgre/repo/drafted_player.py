from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.drafted_player import DraftedPlayerRepositoryProtocol
from src.core.models.drafted_player import DraftedPlayer, DraftedPlayerCreate
from .base import BaseRepository
from ..models import DraftedPlayerModel


class DraftedPlayerRepository(BaseRepository[DraftedPlayerModel, DraftedPlayerCreate, DraftedPlayer, DraftedPlayerCreate], DraftedPlayerRepositoryProtocol):
    model = DraftedPlayerModel
    dto_model = DraftedPlayer

    async def get(
            self,
            field_id: UUID,
            load_draft: bool = False,
            load_player: bool = False
    ) -> DraftedPlayer | None:
        options = []
        if load_draft:
            options.append(selectinload(DraftedPlayerModel.draft))
        if load_player:
            options.append(selectinload(DraftedPlayerModel.event_player))

        return await self._get(field_id, options=options)

    async def list_by_draft(self, draft_id: UUID) -> Sequence[DraftedPlayer]:
        return await self.get_list(
            0, None, None,
            DraftedPlayerModel.draft_id == draft_id
        )
