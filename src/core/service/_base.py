import inspect
from functools import wraps
from typing import Any, Callable
from uuid import UUID

from src.domain.exceptions import ForbiddenException, NotFoundException
from src.infra.postgre.models import Event
from src.infra.postgre.repo import EventRepository, OrganizerRepository


class BaseService:
    _organizer_repo: OrganizerRepository
    _event_repo: EventRepository

    @staticmethod
    def require_organizer(func: Callable) -> Callable:
        sig = inspect.signature(func)

        params = list(sig.parameters.keys())
        if "event_id" not in params or "issuer_id" not in params:
            raise TypeError(
                f"{func.__qualname__} must have 'event_id' and 'issuer_id' parameters"
            )

        @wraps(func)
        async def wrapper(self: BaseService, *args: Any, **kwargs: Any) -> Any:
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()

            event_id = bound.arguments["event_id"]
            issuer_id = bound.arguments["issuer_id"]

            await self._assert_organizer(event_id, issuer_id)
            return await func(self, *args, **kwargs)

        return wrapper

    async def _assert_organizer(self, event_id: UUID, member_id: UUID) -> None:
        organizers = await self._organizer_repo.list_by_event(event_id)
        if not any(o.member_id == member_id for o in organizers):
            raise ForbiddenException("You are not an organizer of this event")

    async def _fetch_event(self, event_id: UUID, **kwargs) -> Event:
        event = await self._event_repo.get(event_id, **kwargs)
        if event is None:
            raise NotFoundException("Event not found")
        return event
