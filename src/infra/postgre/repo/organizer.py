from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.organizer import OrganizerRepositoryProtocol
from src.core.models.organizer import Organizer, OrganizerCreate
from .base import BaseRepository
from ..models import OrganizerModel


class OrganizerRepository(BaseRepository[OrganizerModel, OrganizerCreate, Organizer, OrganizerCreate], OrganizerRepositoryProtocol):
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
