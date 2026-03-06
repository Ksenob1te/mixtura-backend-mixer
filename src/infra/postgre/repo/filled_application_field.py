from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import FilledApplicationField
from .base import BaseRepository


class FilledApplicationFieldRepository(BaseRepository[FilledApplicationField]):
    model = FilledApplicationField

    async def get(
            self,
            field_id: UUID,
            load_application: bool = False,
            load_custom_field: bool = False
    ) -> FilledApplicationField | None:
        options = []
        if load_application:
            options.append(selectinload(FilledApplicationField.application))
        if load_custom_field:
            options.append(selectinload(FilledApplicationField.custom_field))

        return await super()._get(field_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[FilledApplicationField]:
        return await self.list(
            0, None, None,
            FilledApplicationField.application_id == application_id
        )
