from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import StageGroupModel
from .base import BaseRepository


class StageGroupRepository(BaseRepository[StageGroupModel]):
    model = StageGroupModel

    async def get(
            self,
            field_id: UUID,
            load_matches: bool = False
    ) -> StageGroupModel | None:
        options = []
        if load_matches:
            options.append(selectinload(StageGroupModel.matches))

        return await super()._get(field_id, options=options)

    async def list_by_stage(self, stage_id: UUID) -> Sequence[StageGroupModel]:
        return await self.list(
            0, None, None,
            StageGroupModel.stage_id == stage_id
        )
