from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import StageGroup
from .base import BaseRepository


class StageGroupRepository(BaseRepository[StageGroup]):
    model = StageGroup

    async def get(
            self,
            field_id: UUID,
            load_matches: bool = False
    ) -> StageGroup | None:
        options = []
        if load_matches:
            options.append(selectinload(StageGroup.matches))

        return await super()._get(field_id, options=options)

    async def list_by_stage(self, stage_id: UUID) -> Sequence[StageGroup]:
        return await self.list(
            0, None, None,
            StageGroup.stage_id == stage_id
        )
