from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import DraftedPlayerModel
from .base import BaseRepository


class DraftedPlayerRepository(BaseRepository[DraftedPlayerModel]):
    model = DraftedPlayerModel

    async def get(
            self,
            field_id: UUID,
            load_draft: bool = False,
            load_player: bool = False
    ) -> DraftedPlayerModel | None:
        options = []
        if load_draft:
            options.append(selectinload(DraftedPlayerModel.draft))
        if load_player:
            options.append(selectinload(DraftedPlayerModel.event_player))

        return await super()._get(field_id, options=options)

    async def list_by_draft(self, draft_id: UUID) -> Sequence[DraftedPlayerModel]:
        return await self.list(
            0, None, None,
            DraftedPlayerModel.draft_id == draft_id
        )
