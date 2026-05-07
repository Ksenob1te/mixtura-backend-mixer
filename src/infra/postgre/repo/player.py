from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.models.event_player import EventPlayer, EventPlayerCreate, EventPlayerUpdate
from .base import BaseRepository
from ..models import EventPlayerModel


class PlayerRepository(PlayerRepositoryProtocol, BaseRepository[EventPlayerModel, EventPlayerCreate, EventPlayer, EventPlayerUpdate]):
    model = EventPlayerModel
    dto_model = EventPlayer

    async def get(
            self,
            field_id: UUID,
            load_roles: bool = False,
            load_drafted: bool = False
    ) -> EventPlayer | None:
        options = []
        if load_roles:
            options.append(selectinload(EventPlayerModel.player_roles))
        if load_drafted:
            options.append(selectinload(EventPlayerModel.drafted_players))

        return await self._get(field_id, options=options)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> EventPlayer | None:
        stmt = select(EventPlayerModel).where(
            EventPlayerModel.event_id == event_id,
            EventPlayerModel.member_id == member_id,
        )
        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[EventPlayer]:
        return await self.list(
            offset, limit, None,
            EventPlayerModel.event_id == event_id
        )

    async def list_by_event_with_roles(self, event_id: UUID) -> Sequence[EventPlayer]:
        stmt = (
            select(EventPlayerModel)
            .where(EventPlayerModel.event_id == event_id)
            .options(selectinload(EventPlayerModel.player_roles))
        )
        result = await self._session.scalars(stmt)
        return [self._to_dto(item) for item in result.all()]
