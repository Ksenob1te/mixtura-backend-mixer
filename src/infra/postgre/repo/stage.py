from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.stage import StageRepositoryProtocol
from src.core.models.stage import Stage, StageCreate, StageUpdate
from .base import BaseRepository
from ..models import StageModel


class StageRepository(BaseRepository[StageModel, StageCreate, Stage, StageUpdate], StageRepositoryProtocol):
    model = StageModel
    dto_model = Stage

    async def get(
            self,
            field_id: UUID,
            load_groups: bool = False,
            load_settings: bool = False
    ) -> Stage | None:
        options = []
        if load_groups:
            options.append(selectinload(StageModel.groups))
        if load_settings:
            options.extend([
                selectinload(StageModel.round_robin_settings),
                selectinload(StageModel.swiss_settings)
            ])

        return await self._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Stage]:
        return await self.list(
            offset, limit, None,
            StageModel.bracket_id == bracket_id
        )
