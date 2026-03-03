from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Team
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class TeamRepository(BaseRepository):
    async def get_by_id(
            self,
            team_id: UUID,
            load_event: bool = False,
            load_players: bool = False
    ) -> Team | None:
        options = []
        if load_event:
            options.append(selectinload(Team.event))
        if load_players:
            options.append(selectinload(Team.players))

        return await self._session.get(Team, team_id, options=options)

    async def list_by_event(self, event_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Team]:
        stmt = (
            select(Team)
            .where(Team.event_id == event_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, team: Team) -> Team:
        self._session.add(team)
        await self._flush()
        await self._session.refresh(team)
        return team

    async def update(self, team: Team) -> Team:
        team = await self._session.merge(team)
        await self._flush()
        return team

    async def delete(self, team_id: UUID) -> None:
        team = await self.get_by_id(team_id)
        if team:
            await self._session.delete(team)
            await self._flush()
