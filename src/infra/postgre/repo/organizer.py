from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import OrganizerModel
from .base import BaseRepository
from src.core.models.organizer import Organizer

from src.core.interfaces.repo.organizer import OrganizerRepositoryProtocol


class OrganizerRepository(OrganizerRepositoryProtocol, BaseRepository[OrganizerModel, Organizer]):
    model = OrganizerModel
    dto_model = Organizer

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> Organizer | None:
        options = []
        if load_event:
            options.append(selectinload(OrganizerModel.event))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[Organizer]:
        return await self.list(
            0, None, None,
            OrganizerModel.event_id == event_id
        )
