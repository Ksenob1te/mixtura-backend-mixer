from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import SelectedGameRoleModel
from .base import BaseRepository


class SelectedGameRoleRepository(BaseRepository[SelectedGameRoleModel]):
    model = SelectedGameRoleModel

    async def get(
            self,
            field_id: UUID,
            load_player_roles: bool = False,
            load_team_players: bool = False
    ) -> SelectedGameRoleModel | None:
        options = []
        if load_player_roles:
            options.append(selectinload(SelectedGameRoleModel.player_roles))
        if load_team_players:
            options.append(selectinload(SelectedGameRoleModel.team_players))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[SelectedGameRoleModel]:
        return await self.list(
            0, None, None,
            SelectedGameRoleModel.event_id == event_id
        )
