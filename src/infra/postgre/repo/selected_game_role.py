from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.selected_game_role import SelectedGameRoleRepositoryProtocol
from src.core.models.selected_game_role import SelectedGameRole, SelectedGameRoleCreate, SelectedGameRoleUpdate
from .base import BaseRepository
from ..models import SelectedGameRoleModel


class SelectedGameRoleRepository(BaseRepository[SelectedGameRoleModel, SelectedGameRoleCreate, SelectedGameRole, SelectedGameRoleUpdate],
                                 SelectedGameRoleRepositoryProtocol):
    model = SelectedGameRoleModel
    dto_model = SelectedGameRole

    async def get(
            self,
            field_id: UUID,
            load_player_roles: bool = False,
            load_team_players: bool = False
    ) -> SelectedGameRole | None:
        options = []
        if load_player_roles:
            options.append(selectinload(SelectedGameRoleModel.player_roles))
        if load_team_players:
            options.append(selectinload(SelectedGameRoleModel.team_players))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[SelectedGameRole]:
        return await self.get_list(
            0, None, None,
            SelectedGameRoleModel.event_id == event_id
        )
