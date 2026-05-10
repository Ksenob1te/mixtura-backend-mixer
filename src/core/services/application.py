from datetime import datetime, timezone
from uuid import UUID

from src.core.commands.application import (
    GetApplicationCommand,
    ListApplicationsCommand,
    ReviewApplicationCommand,
    SubmitApplicationCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.application import ApplicationRepositoryProtocol
from src.core.interfaces.repo.application_integration import ApplicationIntegrationRepositoryProtocol
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.filled_application_field import FilledApplicationFieldRepositoryProtocol
from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.interfaces.repo.player_role import PlayerRoleRepositoryProtocol
from src.core.models.application import ApplicationCreate, ApplicationStatus, ApplicationUpdate
from src.core.models.application_integration import ApplicationIntegrationCreate
from src.core.models.event import EventMatchType, EventStatus
from src.core.models.event_player import EventPlayerCreate, EventPlayerStatus, EventPlayerUpdate
from src.core.models.filled_application_field import FilledApplicationFieldCreate
from src.core.models.player_role import PlayerRoleCreate
from src.core.results.application import ApplicationListItem, ApplicationIntegrationItem, ApplicationRoleItem
from src.core.interfaces.repo.access import (
    R_MIX_BAN,
    R_TOURNAMENT_BAN,
    P_EVENT_ADMIN_MANAGE_PLAYERS,
    has_restriction,
    has_event_admin_permission,
    is_same_server,
)


class ApplicationService:
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        application_repo: ApplicationRepositoryProtocol,
        player_repo: PlayerRepositoryProtocol,
        player_role_repo: PlayerRoleRepositoryProtocol,
        filled_field_repo: FilledApplicationFieldRepositoryProtocol,
        application_integration_repo: ApplicationIntegrationRepositoryProtocol,
    ):
        self._event_repo = event_repo
        self._application_repo = application_repo
        self._player_repo = player_repo
        self._player_role_repo = player_role_repo
        self._filled_field_repo = filled_field_repo
        self._application_integration_repo = application_integration_repo

    async def submit(self, command: SubmitApplicationCommand) -> dict:
        access = command.access_data

        event = await self._event_repo.get(
            command.event_id,
            load_time_settings=True,
            load_custom_fields=True,
            load_integrations=True,
            load_game_roles=True,
        )
        if not event:
            raise NotFoundException("Event not found")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise BadRequestException("Event is not accepting applications")

        if access.member_id is None:
            raise ForbiddenException("Member identification required")

        if event.server_id != access.server_id:
            raise ForbiddenException("Event belongs to a different server")

        if event.match_type == EventMatchType.SINGLE:
            if has_restriction(access.restriction_mask, R_MIX_BAN):
                raise ForbiddenException("Mix ban prevents participation in single match event")
        elif event.match_type == EventMatchType.TOURNAMENT:
            if has_restriction(access.restriction_mask, R_TOURNAMENT_BAN):
                raise ForbiddenException("Tournament ban prevents participation")

        existing = await self._application_repo.get_by_event_and_member(command.event_id, access.member_id)
        if existing:
            raise ConflictException("Application already exists for this member in this event")

        if event.time_settings:
            now = datetime.now(timezone.utc)
            if event.time_settings.start_time and now < event.time_settings.start_time:
                raise BadRequestException("Application period has not started yet")
            if event.time_settings.end_time and now > event.time_settings.end_time:
                raise BadRequestException("Application period has ended")

        valid_field_ids = {str(f.id) for f in event.custom_fields}
        required_ids = {str(f.id) for f in event.custom_fields if f.is_required}
        provided_field_ids = {str(k) for k in command.filled_fields}

        for fid in command.filled_fields:
            if str(fid) not in valid_field_ids:
                raise BadRequestException(f"Unknown custom field: {fid}")

        missing_required = required_ids - provided_field_ids
        if missing_required:
            raise BadRequestException(f"Missing required custom fields: {missing_required}")

        required_integration_names = {i.name for i in event.required_integrations}
        submitted_integration_names = {i.provider_name for i in command.integrations}
        missing_integrations = required_integration_names - submitted_integration_names
        if missing_integrations:
            raise BadRequestException(f"Missing required integrations: {', '.join(missing_integrations)}")

        role_id_map = {}
        for role in event.selected_game_roles:
            role_id_map[role.id] = role.id
            role_id_map[role.game_role_id] = role.id

        role_priorities = {}
        for role_id, priority in command.role_priorities.items():
            selected_role_id = role_id_map.get(role_id)
            if selected_role_id is None:
                raise BadRequestException(f"Unknown game role: {role_id}")
            role_priorities[str(selected_role_id)] = priority

        application = await self._application_repo.create(
            ApplicationCreate(
                event_id=command.event_id,
                member_id=access.member_id,
                is_approved=not event.use_application,
                status=ApplicationStatus.APPROVED if not event.use_application else ApplicationStatus.PENDING,
            )
        )

        for custom_field_id, value in command.filled_fields.items():
            await self._filled_field_repo.create(
                FilledApplicationFieldCreate(
                    value=value,
                    custom_field_id=custom_field_id,
                    application_id=application.id,
                )
            )

        for integration in command.integrations:
            await self._application_integration_repo.create(
                ApplicationIntegrationCreate(
                    application_id=application.id,
                    user_provider_id=integration.integration_id,
                    provider_id=integration.provider_id,
                    provider_name=integration.provider_name,
                )
            )

        player = await self._player_repo.create(
            EventPlayerCreate(
                event_id=command.event_id,
                member_id=access.member_id,
                application_id=application.id,
            )
        )

        for role_id_str, priority in role_priorities.items():
            await self._player_role_repo.create(
                PlayerRoleCreate(
                    game_role_id=UUID(role_id_str),
                    priority=priority,
                    event_player_id=player.id,
                )
            )

        if event.use_application:
            return {
                "id": str(application.id),
                "status": application.status.value,
                "auto_approved": False,
                "player_id": str(player.id),
            }

        return {
            "id": str(application.id),
            "status": application.status.value,
            "auto_approved": True,
            "player_id": str(player.id),
        }

    async def review(self, command: ReviewApplicationCommand) -> dict:
        application = await self._application_repo.get(
            command.application_id,
            load_filled_fields=True,
            load_integrations=True,
            load_event_player=True,
        )
        if not application:
            raise NotFoundException("Application not found")

        event = await self._event_repo.get(application.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can review applications")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise BadRequestException("Cannot review applications for completed or cancelled event")

        new_status = command.status

        if new_status == ApplicationStatus.APPROVED:
            if event.server_id != access.server_id:
                raise ForbiddenException("Cannot approve application from a different server")

            existing_player = await self._player_repo.get_by_event_and_member(
                application.event_id, application.member_id
            )
            await self._application_repo.update(
                application.id,
                ApplicationUpdate(
                    id=application.id,
                    is_approved=True,
                    status=ApplicationStatus.APPROVED,
                ),
            )

            if existing_player:
                if existing_player.status == EventPlayerStatus.PLAYING:
                    raise ConflictException("EventPlayer is already participating in an active match")
                player = await self._player_repo.update(
                    existing_player.id,
                    EventPlayerUpdate(status=EventPlayerStatus.REGISTERED),
                )
            else:
                player = await self._player_repo.create(
                    EventPlayerCreate(
                        event_id=application.event_id,
                        member_id=application.member_id,
                        application_id=application.id,
                    )
                )

            if command.role_priorities:
                event_with_roles = await self._event_repo.get(application.event_id, load_game_roles=True)
                if not event_with_roles:
                    raise NotFoundException("Event not found")
                role_id_map = {}
                for role in event_with_roles.selected_game_roles:
                    role_id_map[role.id] = role.id
                    role_id_map[role.game_role_id] = role.id

                validated_role_priorities = {}
                for role_id, priority in command.role_priorities.items():
                    selected_role_id = role_id_map.get(role_id)
                    if selected_role_id is None:
                        raise BadRequestException(f"Unknown game role: {role_id}")
                    validated_role_priorities[str(selected_role_id)] = priority

                player_with_roles = await self._player_repo.get(player.id, load_roles=True, load_drafted=False)
                existing_role_ids = {r.game_role_id for r in (player_with_roles.player_roles if player_with_roles else [])}
                for role_id_str, priority in validated_role_priorities.items():
                    role_id = UUID(role_id_str)
                    if role_id in existing_role_ids:
                        continue
                    await self._player_role_repo.create(
                        PlayerRoleCreate(
                            game_role_id=role_id,
                            priority=priority,
                            event_player_id=player.id,
                        )
                    )

            return {"id": str(application.id), "status": "APPROVED", "player_id": str(player.id)}

        elif new_status == ApplicationStatus.REJECTED:
            if application.event_player:
                await self._player_repo.delete(application.event_player.id)

            await self._application_repo.update(
                application.id,
                ApplicationUpdate(
                    id=application.id,
                    is_approved=False,
                    status=ApplicationStatus.REJECTED,
                ),
            )
            return {"id": str(application.id), "status": "REJECTED"}

        elif new_status == ApplicationStatus.WAITLIST:
            await self._application_repo.update(
                application.id,
                ApplicationUpdate(
                    id=application.id,
                    is_approved=False,
                    status=ApplicationStatus.WAITLIST,
                ),
            )
            return {"id": str(application.id), "status": "WAITLIST"}

        else:
            raise BadRequestException(f"Unsupported application status: {new_status}")

    async def get(self, command: GetApplicationCommand) -> dict:
        application = await self._application_repo.get(
            command.application_id,
            load_filled_fields=True,
            load_integrations=True,
            load_event_player=True,
        )
        if not application:
            raise NotFoundException("Application not found")

        access = command.access_data
        event = await self._event_repo.get(application.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        is_own = application.member_id == access.member_id
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
        if not is_organizer and not is_own and not has_admin:
            raise ForbiddenException("Access denied")

        return {
            "id": str(application.id),
            "event_id": str(application.event_id),
            "member_id": str(application.member_id),
            "status": application.status.value,
            "role_priorities": {
                str(pr.game_role_id): pr.priority
                for pr in (application.event_player.player_roles if application.event_player else [])
            },
            "filled_fields": [
                {"custom_field_id": str(f.custom_field_id), "value": f.value}
                for f in application.filled_fields
            ],
            "integrations": [
                {
                    "integration_id": str(i.user_provider_id),
                    "provider_id": str(i.provider_id),
                    "provider_name": i.provider_name,
                }
                for i in application.integrations
            ],
            "event_player_id": str(application.event_player.id) if application.event_player else None,
        }

    async def get_list(self, command: ListApplicationsCommand) -> list[ApplicationListItem]:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can list applications")

        offset = (command.pagination.page - 1) * command.pagination.page_size if command.pagination.page else 0
        limit = command.pagination.page_size

        applications = await self._application_repo.list_by_event(
            command.event_id,
            offset=offset,
            limit=limit,
            status=command.status,
            sort_by=command.sort_by,
            sort_order=command.sort_order,
            load_event_player_with_roles=True,
            load_integrations=True,
        )

        return [
            ApplicationListItem(
                id=a.id,
                member_id=a.member_id,
                status=a.status.value,
                is_approved=a.is_approved,
                created_at=a.created_at,
                roles=[
                    ApplicationRoleItem(
                        role_id=pr.game_role_id,
                        game_role_id=pr.game_role.game_role_id if pr.game_role else None,
                        priority=pr.priority,
                    )
                    for pr in (a.event_player.player_roles if a.event_player else [])
                ],
                integrations=[
                    ApplicationIntegrationItem(
                        integration_id=i.user_provider_id,
                        provider_id=i.provider_id,
                        provider_name=i.provider_name,
                    )
                    for i in a.integrations
                ],
            )
            for a in applications
        ]
