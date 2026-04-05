from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import PlayerRoleModel
from .base import BaseRepository
from src.core.models.player_role import PlayerRole


class PlayerRoleRepository(BaseRepository[PlayerRoleModel, PlayerRole]):
    model = PlayerRoleModel
    dto_model = PlayerRole

    async def get(
            self,
            field_id: UUID,
            load_player: bool = False,
            load_game_role: bool = False
    ) -> PlayerRole | None:
        options = []
        if load_player:
            options.append(selectinload(PlayerRoleModel.event_player))
        if load_game_role:
            options.append(selectinload(PlayerRoleModel.game_role))

        return await self._get(field_id, options=options)

    async def list_by_player(self, player_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[PlayerRole]:
        return await self.list(
            offset, limit, None,
            PlayerRoleModel.event_player_id == player_id
        )
