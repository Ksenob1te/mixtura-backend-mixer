from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Draft
from .base import BaseRepository


class DraftRepository(BaseRepository[Draft]):
    model = Draft

    async def get(
            self,
            field_id: UUID,
            load_drafted_players: bool = False
    ) -> Draft | None:
        options = []
        if load_drafted_players:
            options.append(selectinload(Draft.drafted_players))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Draft]:
        return await self.list(
            offset, limit, None,
            Draft.event_id == event_id
        )
