from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import ApplicationCustomField
from .base import BaseRepository


class ApplicationCustomFieldRepository(BaseRepository[ApplicationCustomField]):
    model = ApplicationCustomField

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> ApplicationCustomField | None:
        options = []
        if load_event:
            options.append(selectinload(ApplicationCustomField.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[ApplicationCustomField]:
        return await self.list(
            0, None, None,
            ApplicationCustomField.event_id == event_id
        )
