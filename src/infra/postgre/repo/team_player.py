from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import TeamPlayer
from .base import BaseRepository


class TeamPlayerRepository(BaseRepository):
    async def get_by_id(
            self,
            player_id: UUID,
            load_team: bool = False,
            load_role: bool = False
    ) -> TeamPlayer | None:
        options = []
        if load_team:
            options.append(selectinload(TeamPlayer.team))
        if load_role:
            options.append(selectinload(TeamPlayer.game_role))

        return await self._session.get(TeamPlayer, player_id, options=options)

    async def list_by_team(self, team_id: UUID) -> Sequence[TeamPlayer]:
        stmt = select(TeamPlayer).where(TeamPlayer.team_id == team_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, player: TeamPlayer) -> TeamPlayer:
        self._session.add(player)
        await self._flush()
        await self._session.refresh(player)
        return player

    async def update(self, player: TeamPlayer) -> TeamPlayer:
        player = await self._session.merge(player)
        await self._flush()
        return player

    async def delete(self, player_id: UUID) -> None:
        player = await self.get_by_id(player_id)
        if player:
            await self._session.delete(player)
            await self._flush()
