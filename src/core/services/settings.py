from datetime import datetime, timezone
from src.core.commands.settings import (
    AddIntegrationCommand,
    RemoveIntegrationCommand,
    AddGameRoleCommand,
    UpdateGameRoleCommand,
    RemoveGameRoleCommand,
    AddCustomFieldCommand,
    UpdateCustomFieldCommand,
    RemoveCustomFieldCommand,
    UpdateTimeSettingsCommand,
    GetApplicationFormSettingsCommand,
)
from src.core.exceptions import BadRequestException, ForbiddenException, NotFoundException, ConflictException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.required_integration import RequiredIntegrationRepositoryProtocol
from src.core.interfaces.repo.selected_game_role import SelectedGameRoleRepositoryProtocol
from src.core.interfaces.repo.application_custom_field import ApplicationCustomFieldRepositoryProtocol
from src.core.interfaces.repo.application_time_settings import ApplicationTimeSettingsRepositoryProtocol
from src.core.models.event import EventStatus
from src.core.models.required_integration import RequiredIntegrationCreate
from src.core.models.selected_game_role import SelectedGameRoleCreate, SelectedGameRoleUpdate
from src.core.models.application_custom_field import ApplicationCustomFieldCreate, ApplicationCustomFieldUpdate
from src.core.models.application_time_settings import ApplicationTimeSettingsCreate, ApplicationTimeSettingsUpdate
from src.core.results.event import (
    EventDetail,
    RequiredIntegrationResponse,
    SelectedGameRoleResponse,
    ApplicationCustomFieldResponse,
    ApplicationTimeSettingsResponse,
    ApplicationFormSettingsResponse,
    OrganizerResponse,
)
from src.core.interfaces.repo.access import (
    P_EVENT_ADMIN_UPDATE,
    has_event_admin_permission,
    is_same_server,
)


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


class SettingsService:
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        integration_repo: RequiredIntegrationRepositoryProtocol,
        role_repo: SelectedGameRoleRepositoryProtocol,
        field_repo: ApplicationCustomFieldRepositoryProtocol,
        time_repo: ApplicationTimeSettingsRepositoryProtocol,
    ):
        self._event_repo = event_repo
        self._integration_repo = integration_repo
        self._role_repo = role_repo
        self._field_repo = field_repo
        self._time_repo = time_repo

    async def add_integration(self, command: AddIntegrationCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        existing = await self._integration_repo.list_by_event(command.event_id)
        if any(i.name.lower() == command.name.lower() for i in existing):
            raise ConflictException("Integration with this name already exists")

        await self._integration_repo.create(
            RequiredIntegrationCreate(name=command.name, event_id=command.event_id)
        )

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def remove_integration(self, command: RemoveIntegrationCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        integration = await self._integration_repo.get(command.integration_id, load_event=False)
        if not integration or integration.event_id != command.event_id:
            raise NotFoundException("Integration not found")

        await self._integration_repo.delete(command.integration_id)

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def add_game_role(self, command: AddGameRoleCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        existing = await self._role_repo.list_by_event(command.event_id)
        if any(r.game_role_id == command.game_role_id for r in existing):
            raise ConflictException("Game role already added to event")

        await self._role_repo.create(
            SelectedGameRoleCreate(
                game_role_id=command.game_role_id,
                event_id=command.event_id,
                override_max_count=command.override_max_count,
                override_min_count=command.override_min_count,
            )
        )

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def update_game_role(self, command: UpdateGameRoleCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        role = await self._role_repo.get(command.selected_role_id, load_player_roles=False, load_team_players=False)
        if not role or role.event_id != command.event_id:
            raise NotFoundException("Selected game role not found")

        update = SelectedGameRoleUpdate(
            id=role.id,
            override_max_count=command.override_max_count,
            override_min_count=command.override_min_count,
        )
        await self._role_repo.update(update)

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def remove_game_role(self, command: RemoveGameRoleCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        role = await self._role_repo.get(command.selected_role_id, load_player_roles=False, load_team_players=False)
        if not role or role.event_id != command.event_id:
            raise NotFoundException("Selected game role not found")

        await self._role_repo.delete(command.selected_role_id)

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def add_custom_field(self, command: AddCustomFieldCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if not event.use_application:
            raise BadRequestException("Event does not use applications")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        existing = await self._field_repo.list_by_event(command.event_id)
        if any(f.name.lower() == command.name.lower() for f in existing):
            raise ConflictException("Custom field with this name already exists")

        await self._field_repo.create(
            ApplicationCustomFieldCreate(
                event_id=command.event_id,
                name=command.name,
                is_private=command.is_private,
                is_required=command.is_required,
            )
        )

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def update_custom_field(self, command: UpdateCustomFieldCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if not event.use_application:
            raise BadRequestException("Event does not use applications")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        field = await self._field_repo.get(command.field_id, load_event=False)
        if not field or field.event_id != command.event_id:
            raise NotFoundException("Custom field not found")

        update = ApplicationCustomFieldUpdate(
            id=field.id,
            name=command.name,
            is_private=command.is_private,
            is_required=command.is_required,
        )
        await self._field_repo.update(update)

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def remove_custom_field(self, command: RemoveCustomFieldCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if not event.use_application:
            raise BadRequestException("Event does not use applications")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        field = await self._field_repo.get(command.field_id, load_event=False)
        if not field or field.event_id != command.event_id:
            raise NotFoundException("Custom field not found")

        await self._field_repo.delete(command.field_id)

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def update_time_settings(self, command: UpdateTimeSettingsCommand) -> EventDetail:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update settings")

        if not event.use_application:
            raise BadRequestException("Event does not use applications")

        if event.status not in (EventStatus.CREATED, EventStatus.IDLE):
            raise BadRequestException("Cannot modify settings after registration opens")

        if command.start_time and command.end_time and command.start_time >= command.end_time:
            raise BadRequestException("Start time must be before end time")

        start_time = command.start_time.astimezone(timezone.utc).replace(tzinfo=None) if command.start_time else None
        end_time = command.end_time.astimezone(timezone.utc).replace(tzinfo=None) if command.end_time else None

        existing = await self._time_repo.get_by_event_id(command.event_id, load_event=False)

        if existing:
            update = ApplicationTimeSettingsUpdate(
                id=existing.id,
                start_time=start_time,
                end_time=end_time,
            )
            await self._time_repo.update(update)
        else:
            await self._time_repo.create(
                ApplicationTimeSettingsCreate(
                    event_id=command.event_id,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        full = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        return _to_detail(full)

    async def get_application_form_settings(self, command: GetApplicationFormSettingsCommand) -> ApplicationFormSettingsResponse:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        if not event.use_application:
            raise BadRequestException("Event does not use applications")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_UPDATE)

        if not is_organizer and not has_admin:
            if event.status != EventStatus.REGISTRATION:
                if event.status in (EventStatus.CREATED, EventStatus.IDLE):
                    raise BadRequestException("Registration not open yet")
                raise BadRequestException("Registration is closed")

        integrations = await self._integration_repo.list_by_event(command.event_id)
        roles = await self._role_repo.list_by_event(command.event_id)
        all_fields = await self._field_repo.list_by_event(command.event_id)
        time_settings = await self._time_repo.get_by_event_id(command.event_id, load_event=False)

        visible_fields = []
        for f in all_fields:
            if access.member_id:
                visible_fields.append(f)
            elif not f.is_private:
                visible_fields.append(f)

        return ApplicationFormSettingsResponse(
            event_id=command.event_id,
            event_name=event.name,
            required_integrations=[
                RequiredIntegrationResponse(id=i.id, name=i.name)
                for i in integrations
            ],
            available_roles=[
                SelectedGameRoleResponse(
                    id=r.id,
                    game_role_id=r.game_role_id,
                    override_max_count=r.override_max_count,
                    override_min_count=r.override_min_count,
                )
                for r in roles
            ],
            custom_fields=[
                ApplicationCustomFieldResponse(
                    id=f.id,
                    name=f.name,
                    is_private=f.is_private,
                    is_required=f.is_required,
                )
                for f in visible_fields
            ],
            time_settings=ApplicationTimeSettingsResponse(
                id=time_settings.id,
                start_time=time_settings.start_time,
                end_time=time_settings.end_time,
            ) if time_settings else None,
        )
