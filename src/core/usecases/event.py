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
from src.core.interfaces.repo.application_time_settings import ApplicationTimeSettingsRepositoryProtocol
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.match import MatchRepositoryProtocol
from src.core.interfaces.repo.organizer import OrganizerRepositoryProtocol
from src.core.models.application_time_settings import ApplicationTimeSettingsCreate
from src.core.models.event import EventCreate, EventUpdate, EventStatus, EventMatchType
from src.core.models.organizer import OrganizerCreate
from src.core.results.event import (
    ApplicationCustomFieldResponse,
    ApplicationTimeSettingsResponse,
    EventCard,
    EventDetail,
    OrganizerResponse,
    RequiredIntegrationResponse,
    SelectedGameRoleResponse,
)
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
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        organizer_repo: OrganizerRepositoryProtocol,
        time_settings_repo: ApplicationTimeSettingsRepositoryProtocol,
    ):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._time_settings_repo = time_settings_repo

    async def __call__(self, command: CreateEventCommand) -> EventDetail:
        access = command.access_data

        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents event creation")

        if access.member_id is None:
            raise ForbiddenException("Member identification required to create event")

        if not has_permission(access.permission_mask, P_EVENT_CREATE):
            raise ForbiddenException("Missing event_create permission")

        event_create = EventCreate(
            name=command.name,
            match_type=command.match_type,
            use_application=command.use_application,
            is_public=command.is_public,
            team_size=command.team_size,
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

        if command.use_application:
            ts_create = ApplicationTimeSettingsCreate(event_id=event.id)
            await self._time_settings_repo.create(ts_create)

        full = await self._event_repo.get(
            event.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


class GetEventUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, command: GetEventCommand) -> EventDetail:
        event = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
        )
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data

        if access is None:
            if not event.is_public:
                raise NotFoundException("Event not found")
            return _to_detail(event)

        if has_server_ban(access):
            raise ForbiddenException("Server ban prevents access")

        same_server = is_same_server(access, event.server_id)
        has_admin_view = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_VIEW)

        if not same_server and not has_admin_view:
            if event.is_public:
                return _to_detail(event)
            raise NotFoundException("Event not found")

        return _to_detail(event)


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
                name=e.name,
                match_type=e.match_type,
                is_public=e.is_public,
                team_size=e.team_size,
                team_formation=e.team_formation,
                status=e.status,
                server_id=e.server_id,
            )
            for e in events
        ]


class ListPrivateEventsUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol):
        self._event_repo = event_repo

    async def __call__(self, command: ListPrivateEventsCommand) -> list[EventCard]:
        offset = (command.pagination.page - 1) * command.pagination.page_size if command.pagination.page else 0
        limit = command.pagination.page_size

        events = await self._event_repo.list_by_server(command.access_data.server_id, offset, limit)

        return [
            EventCard(
                id=e.id,
                name=e.name,
                match_type=e.match_type,
                is_public=e.is_public,
                team_size=e.team_size,
                team_formation=e.team_formation,
                status=e.status,
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
            **command.model_dump(exclude={"access_data", "event_id"}, exclude_unset=True)
        )

        updated = await self._event_repo.update(command.event_id, update)

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


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

        updated = await self._event_repo.transition_status(command.event_id, EventStatus.IDLE)

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


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

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


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

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


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

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


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

        full = await self._event_repo.get(
            updated.id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)


def _to_detail(event) -> EventDetail:
    return EventDetail(
        id=event.id,
        name=event.name,
        match_type=event.match_type,
        use_application=event.use_application,
        is_public=event.is_public,
        team_size=event.team_size,
        team_formation=event.team_formation,
        status=event.status,
        allow_multiple_drafts=event.allow_multiple_drafts,
        rating_set_id=event.rating_set_id,
        server_id=event.server_id,
        organizers=[OrganizerResponse(id=o.id, member_id=o.member_id) for o in (event.organizers or [])],
        required_integrations=[RequiredIntegrationResponse(id=i.id, name=i.name) for i in (event.required_integrations or [])],
        selected_game_roles=[SelectedGameRoleResponse(id=r.id, game_role_id=r.game_role_id, override_max_count=r.override_max_count, override_min_count=r.override_min_count) for r in (event.selected_game_roles or [])],
        time_settings=ApplicationTimeSettingsResponse(id=event.time_settings.id, start_time=event.time_settings.start_time, end_time=event.time_settings.end_time) if event.time_settings else None,
        custom_fields=[ApplicationCustomFieldResponse(id=f.id, name=f.name, is_private=f.is_private, is_required=f.is_required) for f in (event.custom_fields or [])],
    )
