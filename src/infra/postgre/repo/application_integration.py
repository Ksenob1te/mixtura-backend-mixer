from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import ApplicationIntegrationModel
from .base import BaseRepository


class ApplicationIntegrationRepository(BaseRepository[ApplicationIntegrationModel]):
    model = ApplicationIntegrationModel

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False
    ) -> ApplicationIntegrationModel | None:
        options = []
        if load_application:
            options.append(selectinload(ApplicationIntegrationModel.application))

        return await super()._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[ApplicationIntegrationModel]:
        return await self.list(
            0, None, None,
            ApplicationIntegrationModel.application_id == application_id
        )
