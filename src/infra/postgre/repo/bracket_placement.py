from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import BracketPlacement
from .base import BaseRepository


class BracketPlacementRepository(BaseRepository[BracketPlacement]):
    model = BracketPlacement

    async def get(
            self,
            field_id: UUID,
            load_bracket: bool = False
    ) -> BracketPlacement | None:
        options = []
        if load_bracket:
            options.append(selectinload(BracketPlacement.bracket))

        return await super()._get(field_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID) -> Sequence[BracketPlacement]:
        return await self.list(
            0, None, None,
            BracketPlacement.bracket_id == bracket_id
        )
