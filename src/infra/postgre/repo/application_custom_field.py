from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import ApplicationCustomFieldModel
from .base import BaseRepository


class ApplicationCustomFieldRepository(BaseRepository[ApplicationCustomFieldModel]):
    model = ApplicationCustomFieldModel

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> ApplicationCustomFieldModel | None:
        options = []
        if load_event:
            options.append(selectinload(ApplicationCustomFieldModel.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[ApplicationCustomFieldModel]:
        return await self.list(
            0, None, None,
            ApplicationCustomFieldModel.event_id == event_id
        )
