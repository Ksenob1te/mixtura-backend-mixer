from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import DraftedPlayer
from .base import BaseRepository


class DraftedPlayerRepository(BaseRepository[DraftedPlayer]):
    model = DraftedPlayer

    async def get(
            self,
            field_id: UUID,
            load_draft: bool = False,
            load_player: bool = False
    ) -> DraftedPlayer | None:
        options = []
        if load_draft:
            options.append(selectinload(DraftedPlayer.draft))
        if load_player:
            options.append(selectinload(DraftedPlayer.event_player))

        return await super()._get(field_id, options=options)

    async def list_by_draft(self, draft_id: UUID) -> Sequence[DraftedPlayer]:
        return await self.list(
            0, None, None,
            DraftedPlayer.draft_id == draft_id
        )
