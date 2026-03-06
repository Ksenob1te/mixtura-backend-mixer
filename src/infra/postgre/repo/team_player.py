from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import TeamPlayer
from .base import BaseRepository


class TeamPlayerRepository(BaseRepository[TeamPlayer]):
    model = TeamPlayer

    async def get(
            self,
            field_id: UUID,
            load_team: bool = False,
            load_role: bool = False
    ) -> TeamPlayer | None:
        options = []
        if load_team:
            options.append(selectinload(TeamPlayer.team))
        if load_role:
            options.append(selectinload(TeamPlayer.game_role))

        return await super()._get(field_id, options=options)

    async def list_by_team(self, team_id: UUID) -> Sequence[TeamPlayer]:
        return await self.list(
            0, None, None,
            TeamPlayer.team_id == team_id
        )
