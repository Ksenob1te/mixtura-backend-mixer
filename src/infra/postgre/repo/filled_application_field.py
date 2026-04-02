from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import FilledApplicationFieldModel
from .base import BaseRepository


class FilledApplicationFieldRepository(BaseRepository[FilledApplicationFieldModel]):
    model = FilledApplicationFieldModel

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False,
            load_custom_field: bool = False
    ) -> FilledApplicationFieldModel | None:
        options = []
        if load_application:
            options.append(selectinload(FilledApplicationFieldModel.application))
        if load_custom_field:
            options.append(selectinload(FilledApplicationFieldModel.custom_field))

        return await super()._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[FilledApplicationFieldModel]:
        return await self.list(
            0, None, None,
            FilledApplicationFieldModel.application_id == application_id
        )
