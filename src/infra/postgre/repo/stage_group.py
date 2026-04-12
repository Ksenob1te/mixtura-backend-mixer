from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.stage_group import StageGroupRepositoryProtocol
from src.core.models.stage_group import StageGroup
from .base import BaseRepository
from ..models import StageGroupModel


class StageGroupRepository(StageGroupRepositoryProtocol, BaseRepository[StageGroupModel, StageGroup]):
    model = StageGroupModel
    dto_model = StageGroup

    async def get(
            self,
            field_id: UUID,
            load_matches: bool = False
    ) -> StageGroup | None:
        options = []
        if load_matches:
            options.append(selectinload(StageGroupModel.matches))

        return await self._get(field_id, options=options)

    async def list_by_stage(self, stage_id: UUID) -> Sequence[StageGroup]:
        return await self.list(
            0, None, None,
            StageGroupModel.stage_id == stage_id
        )
