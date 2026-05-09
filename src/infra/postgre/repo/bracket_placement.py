from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.bracket_placement import BracketPlacementRepositoryProtocol
from src.core.models.bracket_placement import BracketPlacement, BracketPlacementCreate, BracketPlacementUpdate
from .base import BaseRepository
from ..models import BracketPlacementModel


class BracketPlacementRepository(BaseRepository[BracketPlacementModel, BracketPlacementCreate, BracketPlacement, BracketPlacementUpdate],
                                 BracketPlacementRepositoryProtocol):
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
