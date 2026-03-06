from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Team
from .base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    model = Team

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False,
            load_players: bool = False
    ) -> Team | None:
        options = []
        if load_event:
            options.append(selectinload(Team.event))
        if load_players:
            options.append(selectinload(Team.players))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Team]:
         return await self.list(
            offset, limit, None,
            Team.event_id == event_id
        )
