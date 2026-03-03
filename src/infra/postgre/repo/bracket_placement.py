from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import BracketPlacement
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class BracketPlacementRepository(BaseRepository):
    async def get_by_id(
            self,
            placement_id: UUID,
            load_bracket: bool = False
    ) -> BracketPlacement | None:
        options = []
        if load_bracket:
            options.append(selectinload(BracketPlacement.bracket))

        return await self._session.get(BracketPlacement, placement_id, options=options)

    async def list_by_bracket(self, bracket_id: UUID) -> Sequence[BracketPlacement]:
        stmt = select(BracketPlacement).where(BracketPlacement.bracket_id == bracket_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, placement: BracketPlacement) -> BracketPlacement:
        self._session.add(placement)
        await self._flush()
        await self._session.refresh(placement)
        return placement

    async def update(self, placement: BracketPlacement) -> BracketPlacement:
        placement = await self._session.merge(placement)
        await self._flush()
        return placement

    async def delete(self, placement_id: UUID) -> None:
        placement = await self.get_by_id(placement_id)
        if placement:
            await self._session.delete(placement)
            await self._flush()
