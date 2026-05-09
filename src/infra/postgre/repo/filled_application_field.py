from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.filled_application_field import FilledApplicationFieldRepositoryProtocol
from src.core.models.filled_application_field import FilledApplicationField, FilledApplicationFieldCreate
from .base import BaseRepository
from ..models import FilledApplicationFieldModel


class FilledApplicationFieldRepository(BaseRepository[FilledApplicationFieldModel, FilledApplicationFieldCreate, FilledApplicationField, FilledApplicationFieldCreate],
                                       FilledApplicationFieldRepositoryProtocol):
    model = FilledApplicationFieldModel
    dto_model = FilledApplicationField

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False,
            load_custom_field: bool = False
    ) -> FilledApplicationField | None:
        options = []
        if load_application:
            options.append(selectinload(FilledApplicationFieldModel.application))
        if load_custom_field:
            options.append(selectinload(FilledApplicationFieldModel.custom_field))

        return await self._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[FilledApplicationField]:
        return await self.list(
            0, None, None,
            FilledApplicationFieldModel.application_id == application_id
        )
