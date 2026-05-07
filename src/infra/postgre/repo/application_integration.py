from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.application_integration import ApplicationIntegrationRepositoryProtocol
from src.core.models.application_integration import ApplicationIntegration, ApplicationIntegrationCreate
from .base import BaseRepository
from ..models import ApplicationIntegrationModel


class ApplicationIntegrationRepository(ApplicationIntegrationRepositoryProtocol,
                                       BaseRepository[ApplicationIntegrationModel, ApplicationIntegrationCreate, ApplicationIntegration, ApplicationIntegrationCreate]):
    model = ApplicationIntegrationModel
    dto_model = ApplicationIntegration

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False
    ) -> ApplicationIntegration | None:
        options = []
        if load_application:
            options.append(selectinload(ApplicationIntegrationModel.application))

        return await self._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[ApplicationIntegration]:
        return await self.list(
            0, None, None,
            ApplicationIntegrationModel.application_id == application_id
        )
