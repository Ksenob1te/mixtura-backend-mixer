from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import BracketPlacementModel
from .base import BaseRepository


class BracketPlacementRepository(BaseRepository[BracketPlacementModel]):
    model = BracketPlacementModel

    async def get(
            self,
            field_id: UUID,
            load_bracket: bool = False
    ) -> BracketPlacementModel | None:
        options = []
        if load_bracket:
            options.append(selectinload(BracketPlacementModel.bracket))

        return await super()._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID) -> Sequence[BracketPlacementModel]:
        return await self.list(
            0, None, None,
            BracketPlacementModel.bracket_id == bracket_id
        )
