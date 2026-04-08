from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import RequiredIntegrationModel
from .base import BaseRepository
from src.core.models.required_integration import RequiredIntegration

from src.core.interfaces.repo.required_integration import RequiredIntegrationRepositoryProtocol


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
