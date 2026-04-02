from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import TeamPlayerModel
from .base import BaseRepository


class TeamPlayerRepository(BaseRepository[TeamPlayerModel]):
    model = TeamPlayerModel

    async def get(
            self,
            field_id: UUID,
            load_team: bool = False,
            load_role: bool = False
    ) -> TeamPlayerModel | None:
        options = []
        if load_team:
            options.append(selectinload(TeamPlayerModel.team))
        if load_role:
            options.append(selectinload(TeamPlayerModel.game_role))

        return await super()._get(field_id, options=options)

    async def list_by_team(self, team_id: UUID) -> Sequence[TeamPlayerModel]:
        return await self.list(
            0, None, None,
            TeamPlayerModel.team_id == team_id
        )
