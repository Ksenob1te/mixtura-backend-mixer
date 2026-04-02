from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import TeamModel
from .base import BaseRepository


class TeamRepository(BaseRepository[TeamModel]):
    model = TeamModel

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False,
            load_players: bool = False
    ) -> TeamModel | None:
        options = []
        if load_event:
            options.append(selectinload(TeamModel.event))
        if load_players:
            options.append(selectinload(TeamModel.players))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[TeamModel]:
         return await self.list(
            offset, limit, None,
            TeamModel.event_id == event_id
        )
