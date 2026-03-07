from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import EventPlayer
from .base import BaseRepository


class PlayerRepository(BaseRepository[EventPlayer]):
    model = EventPlayer

    async def get(
            self,
            field_id: UUID,
            load_roles: bool = False,
            load_drafted: bool = False
    ) -> EventPlayer | None:
        options = []
        if load_roles:
            options.append(selectinload(EventPlayer.player_roles))
        if load_drafted:
            options.append(selectinload(EventPlayer.drafted_players))

        return await super()._get(field_id, options=options)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> EventPlayer | None:
        stmt = select(EventPlayer).where(
            EventPlayer.event_id == event_id,
            EventPlayer.member_id == member_id,
        )
        return await self._session.scalar(stmt)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[EventPlayer]:
        return await self.list(
            offset, limit, None,
            EventPlayer.event_id == event_id
        )

    async def list_by_event_with_roles(self, event_id: UUID) -> Sequence[EventPlayer]:
        stmt = (
            select(EventPlayer)
            .where(EventPlayer.event_id == event_id)
            .options(selectinload(EventPlayer.player_roles))
        )
        result = await self._session.scalars(stmt)
        return result.all()

