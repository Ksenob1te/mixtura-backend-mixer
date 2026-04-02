from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import StageModel
from .base import BaseRepository


class StageRepository(BaseRepository[StageModel]):
    model = StageModel

    async def get(
            self,
            field_id: UUID,
            load_groups: bool = False,
            load_settings: bool = False
    ) -> StageModel | None:
        options = []
        if load_groups:
            options.append(selectinload(StageModel.groups))
        if load_settings:
            options.extend([
                selectinload(StageModel.round_robin_settings),
                selectinload(StageModel.swiss_settings)
            ])

        return await super()._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[StageModel]:
        return await self.list(
            offset, limit, None,
            StageModel.bracket_id == bracket_id
        )
