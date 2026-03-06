from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Stage
from .base import BaseRepository


class StageRepository(BaseRepository[Stage]):
    model = Stage

    async def get(
            self,
            field_id: UUID,
            load_groups: bool = False,
            load_settings: bool = False
    ) -> Stage | None:
        options = []
        if load_groups:
            options.append(selectinload(Stage.groups))
        if load_settings:
            options.extend([
                selectinload(Stage.round_robin_settings),
                selectinload(Stage.swiss_settings)
            ])

        return await super()._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Stage]:
        return await self.list(
            offset, limit, None,
            Stage.bracket_id == bracket_id
        )
