from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import Draft, DraftedPlayer
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class DraftRepository(BaseRepository):
    async def get_by_id(
            self,
            draft_id: UUID,
            load_drafted_players: bool = False
    ) -> Draft | None:
        options = []
        if load_drafted_players:
            options.append(selectinload(Draft.drafted_players))

        return await self._session.get(Draft, draft_id, options=options)

    async def list_by_event(self, event_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Draft]:
        stmt = (
            select(Draft)
            .where(Draft.event_id == event_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, draft: Draft) -> Draft:
        self._session.add(draft)
        await self._flush()
        await self._session.refresh(draft)
        return draft

    async def update(self, draft: Draft) -> Draft:
        draft = await self._session.merge(draft)
        await self._flush()
        return draft

    async def delete(self, draft_id: UUID) -> None:
        draft = await self.get_by_id(draft_id)
        if draft:
            await self._session.delete(draft)
            await self._flush()

    async def add_player(self, player: DraftedPlayer) -> DraftedPlayer:
        self._session.add(player)
        await self._flush()
        await self._session.refresh(player)
        return player

    async def remove_player(self, draft_id: UUID, event_player_id: UUID) -> None:
        stmt = select(DraftedPlayer).where(
            DraftedPlayer.draft_id == draft_id,
            DraftedPlayer.event_player_id == event_player_id
        )
        player = await self._session.scalar(stmt)
        if player:
            await self._session.delete(player)
            await self._flush()
