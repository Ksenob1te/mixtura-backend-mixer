from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.required_integration import RequiredIntegrationRepositoryProtocol
from src.core.models.required_integration import RequiredIntegration
from .base import BaseRepository
from ..models import RequiredIntegrationModel


class RequiredIntegrationRepository(RequiredIntegrationRepositoryProtocol,
                                    BaseRepository[RequiredIntegrationModel, RequiredIntegration]):
    model = RequiredIntegrationModel
    dto_model = RequiredIntegration

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> RequiredIntegration | None:
        options = []
        if load_event:
            options.append(selectinload(RequiredIntegrationModel.event))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[RequiredIntegration]:
        return await self.list(
            0, None, None,
            RequiredIntegrationModel.event_id == event_id
        )
