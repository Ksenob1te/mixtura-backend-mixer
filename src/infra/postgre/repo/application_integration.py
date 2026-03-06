from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import ApplicationIntegration
from .base import BaseRepository


class ApplicationIntegrationRepository(BaseRepository[ApplicationIntegration]):
    model = ApplicationIntegration

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False
    ) -> ApplicationIntegration | None:
        options = []
        if load_application:
            options.append(selectinload(ApplicationIntegration.application))

        return await super()._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[ApplicationIntegration]:
        return await self.list(
            0, None, None,
            ApplicationIntegration.application_id == application_id
        )
