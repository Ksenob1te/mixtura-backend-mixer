from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload

from ..models import Event
from .base import BaseRepository


class EventRepository(BaseRepository[Event]):
    model = Event

    async def get(
            self,
            field_id: UUID,
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

        return await super()._get(field_id, options=options)

    async def list_public(self, offset: int, limit: int) -> Sequence[Event]:
        return await self.list(
            offset, limit, None,
            Event.is_public.is_(True)
        )
        return await self.list(0, 1000, None, Event.status == status)
