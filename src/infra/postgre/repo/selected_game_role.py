from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import SelectedGameRole
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class SelectedGameRoleRepository(BaseRepository):
    async def get_by_id(
            self,
            role_id: UUID,
            load_player_roles: bool = False,
            load_team_players: bool = False
    ) -> SelectedGameRole | None:
        options = []
        if load_player_roles:
            options.append(selectinload(SelectedGameRole.player_roles))
        if load_team_players:
            options.append(selectinload(SelectedGameRole.team_players))

        return await self._session.get(SelectedGameRole, role_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[SelectedGameRole]:
        stmt = select(SelectedGameRole).where(SelectedGameRole.event_id == event_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, role: SelectedGameRole) -> SelectedGameRole:
        self._session.add(role)
        await self._flush()
        await self._session.refresh(role)
        return role

    async def update(self, role: SelectedGameRole) -> SelectedGameRole:
        role = await self._session.merge(role)
        await self._flush()
        return role

    async def delete(self, role_id: UUID) -> None:
        role = await self.get_by_id(role_id)
        if role:
            await self._session.delete(role)
            await self._flush()
