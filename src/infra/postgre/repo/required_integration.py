from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import RequiredIntegration
from .base import BaseRepository


class RequiredIntegrationRepository(BaseRepository[RequiredIntegration]):
    model = RequiredIntegration

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> RequiredIntegration | None:
        options = []
        if load_event:
            options.append(selectinload(RequiredIntegration.event))

        return await super()._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[RequiredIntegration]:
        return await self.list(
            0, None, None,
            RequiredIntegration.event_id == event_id
        )
