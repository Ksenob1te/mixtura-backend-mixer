from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import DraftedPlayer
from .base import BaseRepository


class DraftedPlayerRepository(BaseRepository):
    async def get_by_id(
            self,
            drafted_id: UUID,
            load_draft: bool = False,
            load_player: bool = False
    ) -> DraftedPlayer | None:
        options = []
        if load_draft:
            options.append(selectinload(DraftedPlayer.draft))
        if load_player:
            options.append(selectinload(DraftedPlayer.event_player))

        return await self._session.get(DraftedPlayer, drafted_id, options=options)

    async def list_by_draft(self, draft_id: UUID) -> Sequence[DraftedPlayer]:
        stmt = select(DraftedPlayer).where(DraftedPlayer.draft_id == draft_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, player: DraftedPlayer) -> DraftedPlayer:
        self._session.add(player)
        await self._flush()
        await self._session.refresh(player)
        return player

    async def update(self, player: DraftedPlayer) -> DraftedPlayer:
        player = await self._session.merge(player)
        await self._flush()
        return player

    async def delete(self, drafted_id: UUID) -> None:
        player = await self.get_by_id(drafted_id)
        if player:
            await self._session.delete(player)
            await self._flush()
