"""Shared authorization helpers reused across domain services."""

from __future__ import annotations

from uuid import UUID

from src.domain.exceptions import ForbiddenException, NotFoundException
from src.infra.postgre.models import Event
from src.infra.postgre.repo import EventRepository, OrganizerRepository


class BaseService:
    """
    Mixin that provides organizer authorization.

    Any service that needs ``_assert_organizer`` should inherit from this

    Require OrganizerRepository and EventRepository in ``__init__``.
    """

    _organizer_repo: OrganizerRepository
    _event_repo: EventRepository

    async def _assert_organizer(self, event_id: UUID, member_id: UUID) -> None:
        """Raise ``ForbiddenException`` unless *member_id* is an organizer of *event_id*."""
        organizers = await self._organizer_repo.list_by_event(event_id)
        if not any(o.member_id == member_id for o in organizers):
            raise ForbiddenException("You are not an organizer of this event")

    async def _fetch_event(self, event_id: UUID, **kwargs) -> Event:
        """
        Fetch event by id or raise ``NotFoundException``.

        :raises NotFoundException: if event is not found.
        """
        event = await self._event_repo.get(event_id, **kwargs)
        if event is None:
            raise NotFoundException("Event not found")
        return event

