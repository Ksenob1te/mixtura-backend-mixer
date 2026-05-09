from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.application_custom_field import ApplicationCustomFieldRepositoryProtocol
from src.core.models.application_custom_field import ApplicationCustomField, ApplicationCustomFieldCreate, ApplicationCustomFieldUpdate
from .base import BaseRepository
from ..models import ApplicationCustomFieldModel


class ApplicationCustomFieldRepository(BaseRepository[ApplicationCustomFieldModel, ApplicationCustomFieldCreate, ApplicationCustomField, ApplicationCustomFieldUpdate],
                                       ApplicationCustomFieldRepositoryProtocol):
    model = ApplicationCustomFieldModel
    dto_model = ApplicationCustomField

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False
    ) -> ApplicationCustomField | None:
        options = []
        if load_event:
            options.append(selectinload(ApplicationCustomFieldModel.event))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[ApplicationCustomField]:
        return await self.list(
            0, None, None,
            ApplicationCustomFieldModel.event_id == event_id
        )
