from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import EventPlayer
from .base import BaseRepository


class PlayerRepository(BaseRepository[EventPlayer]):
    model = EventPlayer

    async def get(
            self,
            field_id: UUID,
            load_roles: bool = False,
            load_drafted: bool = False
    ) -> EventPlayer | None:
        options = []
        if load_roles:
            options.append(selectinload(EventPlayer.player_roles))
        if load_drafted:
            options.append(selectinload(EventPlayer.drafted_players))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[EventPlayer]:
        return await self.list(
            offset, limit, None,
            EventPlayer.event_id == event_id
        )
