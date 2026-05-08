from src.core.commands.event import (
    CreateEventCommand,
    GetEventCommand,
    ListPublicEventsCommand,
    ListPrivateEventsCommand,
    UpdateEventCommand,
    ActivateEventCommand,
    OpenRegistrationCommand,
    CloseRegistrationCommand,
    CancelEventCommand,
    CompleteEventCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.match import MatchRepositoryProtocol
from src.core.interfaces.repo.organizer import OrganizerRepositoryProtocol
from src.core.models.event import EventCreate, EventUpdate, EventStatus, EventMatchType
from src.core.models.organizer import OrganizerCreate
from src.core.results.event import EventCard, EventDetail
from src.core.usecases._access import (
    P_EVENT_CREATE,
    P_EVENT_ADMIN_VIEW,
    P_EVENT_ADMIN_UPDATE,
    P_EVENT_ADMIN_CANCEL,
    P_EVENT_ADMIN_COMPLETE,
    has_permission,
    has_event_admin_permission,
    has_server_ban,
    is_same_server,
)


class CreateEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: CreateEventCommand) -> EventCard:
        access = command.access_data

        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event creation")

        if access.member_id is None:
            raise ForbiddenException("Member identification required to create event")
        print(access.permission_mask)
        if not has_permission(access.permission_mask, P_EVENT_CREATE):
            raise ForbiddenException("Missing event_create permission")

        event_create = EventCreate(
            match_type=command.match_type,
            use_application=command.use_application,
            is_public=command.is_public,
            team_size=command.team_size,
            registration_type=command.registration_type,
            team_formation=command.team_formation,
            allow_multiple_drafts=command.allow_multiple_drafts,
            rating_set_id=command.rating_set_id,
            server_id=access.server_id,
        )

        event = await self._event_repo.create(event_create)

        organizer_create = OrganizerCreate(
            event_id=event.id,
            member_id=access.member_id,
        )
        await self._organizer_repo.create(organizer_create)

        return EventCard(
            id=event.id,
            match_type=event.match_type,
            is_public=event.is_public,
            team_size=event.team_size,
            registration_type=event.registration_type,
            team_formation=event.team_formation,
            status=event.status,
            server_id=event.server_id,
        )


class GetEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: GetEventCommand) -> EventCard | EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data

        if access is None:
            if not event.is_public:
                raise NotFoundException("Event not found")
            return EventCard(
                id=event.id,
                match_type=event.match_type,
                is_public=event.is_public,
                team_size=event.team_size,
                registration_type=event.registration_type,
                team_formation=event.team_formation,
                status=event.status,
                server_id=event.server_id,
            )

        same_server = is_same_server(access, event.server_id)
        is_organizer = same_server and any(o.member_id == access.member_id for o in event.organizers)
        has_admin_view = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_VIEW)

        if not is_organizer and not has_admin_view:
            if event.is_public:
                return EventCard(
                    id=event.id,
                    match_type=event.match_type,
                    is_public=event.is_public,
                    team_size=event.team_size,
                    registration_type=event.registration_type,
                    team_formation=event.team_formation,
                    status=event.status,
                    server_id=event.server_id,
                )
            raise NotFoundException("Event not found")

        return EventDetail(
            id=event.id,
            match_type=event.match_type,
            use_application=event.use_application,
            is_public=event.is_public,
            team_size=event.team_size,
            registration_type=event.registration_type,
            team_formation=event.team_formation,
            status=event.status,
            allow_multiple_drafts=event.allow_multiple_drafts,
            rating_set_id=event.rating_set_id,
            server_id=event.server_id,
        )


class ListPublicEventsUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol):
        self._event_repo = event_repo

    async def __call__(self, command: ListPublicEventsCommand) -> list[EventCard]:
        offset = (command.pagination.page - 1) * command.pagination.page_size if command.pagination.page else 0
        limit = command.pagination.page_size

        events = await self._event_repo.list_public_by_server(command.server_id, offset, limit)

        return [
            EventCard(
                id=e.id,
                match_type=e.match_type,
                is_public=e.is_public,
                team_size=e.team_size,
                registration_type=e.registration_type,
                team_formation=e.team_formation,
                status=e.status,
                server_id=e.server_id,
            )
            for e in events
        ]


class ListPrivateEventsUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol):
        self._event_repo = event_repo

    async def __call__(self, command: ListPrivateEventsCommand) -> list[EventDetail]:
        offset = (command.pagination.page - 1) * command.pagination.page_size if command.pagination.page else 0
        limit = command.pagination.page_size

        events = await self._event_repo.list_by_server(command.access_data.server_id, offset, limit)

        return [
            EventDetail(
                id=e.id,
                match_type=e.match_type,
                use_application=e.use_application,
                is_public=e.is_public,
                team_size=e.team_size,
                registration_type=e.registration_type,
                team_formation=e.team_formation,
                status=e.status,
                allow_multiple_drafts=e.allow_multiple_drafts,
                rating_set_id=e.rating_set_id,
                server_id=e.server_id,
            )
            for e in events
        ]


class UpdateEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: UpdateEventCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event update")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update event")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Event can only be updated before registration opens")

        update = EventUpdate(
            match_type=command.match_type,
            use_application=command.use_application,
            is_public=command.is_public,
            team_size=command.team_size,
            registration_type=command.registration_type,
            team_formation=command.team_formation,
            allow_multiple_drafts=command.allow_multiple_drafts,
            rating_set_id=command.rating_set_id,
        )

        updated = await self._event_repo.update(command.event_id, update)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )


class ActivateEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: ActivateEventCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event activation")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can activate event")

        if event.match_type == EventMatchType.SINGLE:
            updated = await self._event_repo.transition_status(command.event_id, EventStatus.IDLE)
        else:
            updated = await self._event_repo.transition_status(command.event_id, EventStatus.IDLE)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )


class OpenRegistrationUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: OpenRegistrationCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents registration management")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can open registration")

        updated = await self._event_repo.transition_status(command.event_id, EventStatus.REGISTRATION)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )


class CloseRegistrationUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: CloseRegistrationCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents registration management")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can close registration")

        updated = await self._event_repo.transition_status(command.event_id, EventStatus.IDLE)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )


class CancelEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: CancelEventCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event cancellation")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_CANCEL)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can cancel event")

        updated = await self._event_repo.transition_status(command.event_id, EventStatus.CANCELLED)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )


class CompleteSingleGameEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, match_repo: MatchRepositoryProtocol):
        self._event_repo = event_repo
        self._match_repo = match_repo

    async def __call__(self, command: CompleteEventCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event completion")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_COMPLETE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can complete event")
        if event.match_type != EventMatchType.SINGLE:
            raise BadRequestException("This completion command is only for single-game events")
        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise ConflictException(f"Event status {event.status.value} cannot be completed")

        active_matches = await self._match_repo.count_incomplete_matches_by_event(command.event_id)
        if active_matches > 0:
            raise ConflictException("Cannot complete event while active matches exist")

        updated = await self._event_repo.transition_status(command.event_id, EventStatus.COMPLETED)

        return EventDetail(
            id=updated.id,
            match_type=updated.match_type,
            use_application=updated.use_application,
            is_public=updated.is_public,
            team_size=updated.team_size,
            registration_type=updated.registration_type,
            team_formation=updated.team_formation,
            status=updated.status,
            allow_multiple_drafts=updated.allow_multiple_drafts,
            rating_set_id=updated.rating_set_id,
            server_id=updated.server_id,
        )
