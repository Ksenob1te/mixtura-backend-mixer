from uuid import UUID
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import (
    Event,
    Organizer,
    RequiredIntegration,
    SelectedGameRole
)
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class EventRepository(BaseRepository):
    async def get_by_id(
            self,
            event_id: UUID,
            load_organizers: bool = False,
            load_integrations: bool = False,
            load_time_settings: bool = False,
            load_game_roles: bool = False,
            load_custom_fields: bool = False,
            load_applications: bool = False,
            load_teams: bool = False,
            load_drafts: bool = False,
            load_players: bool = False,
            load_brackets: bool = False
    ) -> Event | None:
        options = []
        if load_organizers:
            options.append(selectinload(Event.organizers))
        if load_integrations:
            options.append(selectinload(Event.required_integrations))
        if load_time_settings:
            options.append(selectinload(Event.time_settings))
        if load_game_roles:
            options.append(selectinload(Event.selected_game_roles))
        if load_custom_fields:
            options.append(selectinload(Event.custom_fields))
        if load_applications:
            options.append(selectinload(Event.applications))
        if load_teams:
            options.append(selectinload(Event.teams))
        if load_drafts:
            options.append(selectinload(Event.drafts))
        if load_players:
            options.append(selectinload(Event.event_players))
        if load_brackets:
            options.append(selectinload(Event.brackets))

        return await self._session.get(Event, event_id, options=options)

    async def create(self, event: Event) -> Event:
        self._session.add(event)
        await self._flush()
        await self._session.refresh(event)
        return event

    async def update(self, event: Event) -> Event:
        event = await self._session.merge(event)
        await self._flush()
        return event

    async def delete(self, event_id: UUID) -> None:
        event = await self.get_by_id(event_id)
        if event:
            await self._session.delete(event)
            await self._flush()

    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Event]:
        stmt = select(Event).offset(skip).limit(limit)
        result = await self._session.scalars(stmt)
        return result.all()
