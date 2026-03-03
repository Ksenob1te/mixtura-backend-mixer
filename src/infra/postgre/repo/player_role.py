from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import PlayerRole
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class PlayerRoleRepository(BaseRepository):
    async def get_by_id(
            self,
            role_id: UUID,
            load_player: bool = False,
            load_game_role: bool = False
    ) -> PlayerRole | None:
        options = []
        if load_player:
            options.append(selectinload(PlayerRole.event_player))
        if load_game_role:
            options.append(selectinload(PlayerRole.game_role))

        return await self._session.get(PlayerRole, role_id, options=options)

    async def list_by_player(self, player_id: UUID) -> Sequence[PlayerRole]:
        stmt = select(PlayerRole).where(PlayerRole.event_player_id == player_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, role: PlayerRole) -> PlayerRole:
        self._session.add(role)
        await self._flush()
        await self._session.refresh(role)
        return role

    async def update(self, role: PlayerRole) -> PlayerRole:
        role = await self._session.merge(role)
        await self._flush()
        return role

    async def delete(self, role_id: UUID) -> None:
        role = await self.get_by_id(role_id)
        if role:
            await self._session.delete(role)
            await self._flush()
