from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Organizer
from .base import BaseRepository


class OrganizerRepository(BaseRepository[Organizer]):
    model = Organizer

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> Organizer | None:
        options = []
        if load_event:
            options.append(selectinload(Organizer.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[Organizer]:
        return await self.list(
            0, None, None,
            Organizer.event_id == event_id
        )
