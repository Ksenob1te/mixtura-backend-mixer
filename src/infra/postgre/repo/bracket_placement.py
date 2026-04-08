from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import BracketPlacementModel
from .base import BaseRepository
from src.core.models.bracket_placement import BracketPlacement

from src.core.interfaces.repo.bracket_placement import BracketPlacementRepositoryProtocol


class BracketPlacementRepository(BracketPlacementRepositoryProtocol,
                                 BaseRepository[BracketPlacementModel, BracketPlacement]):
    model = BracketPlacementModel
    dto_model = BracketPlacement

    async def get(
            self,
            field_id: UUID,
            load_bracket: bool = False
    ) -> BracketPlacement | None:
        options = []
        if load_bracket:
            options.append(selectinload(BracketPlacementModel.bracket))

        return await self._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID) -> Sequence[BracketPlacement]:
        return await self.list(
            0, None, None,
            BracketPlacementModel.bracket_id == bracket_id
        )
