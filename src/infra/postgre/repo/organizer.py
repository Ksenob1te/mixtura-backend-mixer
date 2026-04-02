from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import OrganizerModel
from .base import BaseRepository


class OrganizerRepository(BaseRepository[OrganizerModel]):
    model = OrganizerModel

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> OrganizerModel | None:
        options = []
        if load_event:
            options.append(selectinload(OrganizerModel.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[OrganizerModel]:
        return await self.list(
            0, None, None,
            OrganizerModel.event_id == event_id
        )
