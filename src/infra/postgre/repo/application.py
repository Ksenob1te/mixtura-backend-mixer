from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Application
from .base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    model = Application

    async def get(
            self,
            field_id: UUID,
            load_filled_fields: bool = False,
            load_integrations: bool = False,
            load_event_player: bool = False
    ) -> Application | None:
        options = []
        if load_filled_fields:
            options.append(selectinload(Application.filled_fields))
        if load_integrations:
            options.append(selectinload(Application.integrations))
        if load_event_player:
            options.append(selectinload(Application.event_player))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Application]:
        return await self.list(
            offset, limit, None,
            Application.event_id == event_id
        )
