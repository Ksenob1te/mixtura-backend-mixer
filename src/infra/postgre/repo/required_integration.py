from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import RequiredIntegrationModel
from .base import BaseRepository


class RequiredIntegrationRepository(BaseRepository[RequiredIntegrationModel]):
    model = RequiredIntegrationModel

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> RequiredIntegrationModel | None:
        options = []
        if load_event:
            options.append(selectinload(RequiredIntegrationModel.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[RequiredIntegrationModel]:
        return await self.list(
            0, None, None,
            RequiredIntegrationModel.event_id == event_id
        )
