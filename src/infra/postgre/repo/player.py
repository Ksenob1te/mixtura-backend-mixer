from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import EventPlayer, PlayerRole
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class PlayerRepository(BaseRepository):
    async def get_by_id(
            self,
            player_id: UUID,
            load_roles: bool = False,
            load_drafted: bool = False
    ) -> EventPlayer | None:
        options = []
        if load_roles:
            options.append(selectinload(EventPlayer.player_roles))
        if load_drafted:
            options.append(selectinload(EventPlayer.drafted_players))

        return await self._session.get(EventPlayer, player_id, options=options)

    async def list_by_event(self, event_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[EventPlayer]:
        stmt = (
            select(EventPlayer)
            .where(EventPlayer.event_id == event_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, player: EventPlayer) -> EventPlayer:
        self._session.add(player)
        await self._flush()
        await self._session.refresh(player)
        return player

    async def update(self, player: EventPlayer) -> EventPlayer:
        player = await self._session.merge(player)
        await self._flush()
        return player

    async def delete(self, player_id: UUID) -> None:
        player = await self.get_by_id(player_id)
        if player:
            await self._session.delete(player)
            await self._flush()
