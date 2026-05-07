from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.models.event import Event, EventCreate, EventUpdate, EventStatus
from .base import BaseRepository
from ..models import EventModel


class EventRepository(EventRepositoryProtocol, BaseRepository[EventModel, EventCreate, Event, EventUpdate]):
    model = EventModel
    dto_model = Event

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
            options.append(selectinload(EventModel.organizers))
        if load_integrations:
            options.append(selectinload(EventModel.required_integrations))
        if load_time_settings:
            options.append(selectinload(EventModel.time_settings))
        if load_game_roles:
            options.append(selectinload(EventModel.selected_game_roles))
        if load_custom_fields:
            options.append(selectinload(EventModel.custom_fields))
        if load_applications:
            options.append(selectinload(EventModel.applications))
        if load_teams:
            options.append(selectinload(EventModel.teams))
        if load_drafts:
            options.append(selectinload(EventModel.drafts))
        if load_players:
            options.append(selectinload(EventModel.event_players))
        if load_brackets:
            options.append(selectinload(EventModel.brackets))

        return await self._get(field_id, options=options)

    async def list_public(self, offset: int, limit: int) -> Sequence[Event]:
        return await self.list(
            offset, limit, None,
            EventModel.is_public.is_(True)
        )

    async def update(self, event_id: UUID, dto: EventUpdate) -> Event:  # type: ignore[override]
        obj = await self._get_model(event_id)
        if not obj:
            raise NotFoundException("Event not found")
        update_data = self._dto_to_data(dto, exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self._flush()
        await self._session.refresh(obj)
        return self._to_dto(obj)

    async def transition_status(self, event_id: UUID, new_status: EventStatus) -> Event:
        obj = await self._get_model(event_id)
        if not obj:
            raise NotFoundException("Event not found")
        obj.transition_to(new_status)
        await self._flush()
        await self._session.refresh(obj)
        return self._to_dto(obj)
