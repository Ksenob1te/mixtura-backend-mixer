from uuid import UUID

from src.core.commands.player import (
    AddPlayerCommand,
    GetBulkPlayersCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    UpdatePlayerRolesCommand,
    UpdatePlayerStatusCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.interfaces.repo.player_role import PlayerRoleRepositoryProtocol
from src.core.models.event import EventStatus
from src.core.models.event_player import EventPlayerCreate, EventPlayerStatus, EventPlayerUpdate
from src.core.models.player_role import PlayerRoleCreate, PlayerRoleUpdate
from src.core.results.player import (
    PlayerAddResult,
    PlayerItem,
    PlayerRoleItem,
    PlayerRolesUpdateResult,
    PlayerUpdateResult,
)
from src.core.interfaces.repo.access import (
    P_EVENT_ADMIN_MANAGE_PLAYERS,
    has_event_admin_permission,
    is_same_server,
)


class PlayerService:
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        player_repo: PlayerRepositoryProtocol,
        player_role_repo: PlayerRoleRepositoryProtocol,
    ):
        self._event_repo = event_repo
        self._player_repo = player_repo
        self._player_role_repo = player_role_repo

    async def get_list(self, command: ListPlayersCommand) -> list[PlayerItem]:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can list players")

        offset = (command.pagination.page - 1) * command.pagination.page_size if command.pagination.page else 0
        limit = command.pagination.page_size

        players = await self._player_repo.list_by_event(
            command.event_id, offset=offset, limit=limit, status=command.status
        )

        return [PlayerItem.model_validate(p) for p in players]

    async def update_status(self, command: UpdatePlayerStatusCommand) -> PlayerUpdateResult:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update player status")

        if event.status == EventStatus.CANCELLED:
            raise BadRequestException("Cannot modify players in a cancelled event")

        player = await self._player_repo.get_by_event_and_member(command.event_id, command.member_id)
        if not player:
            raise NotFoundException("EventPlayer not found")

        if player.status == EventPlayerStatus.PLAYING:
            if command.status != EventPlayerStatus.PLAYING:
                raise BadRequestException(
                    "Cannot change status of a player currently in an active match"
                )

        player = await self._player_repo.update(
            player.id,
            EventPlayerUpdate(status=command.status, custom_id=command.custom_id),
        )

        return PlayerUpdateResult.model_validate(player)

    async def add(self, command: AddPlayerCommand) -> PlayerAddResult:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can add players")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise BadRequestException("Cannot add players to a completed or cancelled event")

        existing = await self._player_repo.get_by_event_and_member(command.event_id, command.member_id)
        if existing:
            raise ConflictException("Player already exists in this event")

        player = await self._player_repo.create(
            EventPlayerCreate(
                event_id=command.event_id,
                member_id=command.member_id,
                custom_id=command.custom_id,
                is_draft_pinned=command.is_draft_pinned,
            )
        )

        return PlayerAddResult.model_validate(player)

    async def update_roles(self, command: UpdatePlayerRolesCommand) -> PlayerRolesUpdateResult:
        event = await self._event_repo.get(
            command.event_id,
            load_organizers=True,
            load_game_roles=True,
        )
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can update player roles")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise BadRequestException("Cannot update player roles in a completed or cancelled event")

        player = await self._player_repo.get_by_event_and_member(command.event_id, command.member_id)
        if not player:
            raise NotFoundException("EventPlayer not found")

        role_id_map = {}
        for role in event.selected_game_roles:
            role_id_map[role.id] = role.id
            role_id_map[role.game_role_id] = role.id

        for rp in command.role_priorities:
            if rp.role_id not in role_id_map:
                raise BadRequestException(f"Unknown game role: {rp.role_id}")

        duplicate_check: dict[str, int] = {}
        for rp in command.role_priorities:
            selected_role_id_str = str(role_id_map[rp.role_id])
            if selected_role_id_str in duplicate_check:
                raise BadRequestException(f"Duplicate game role priority: {rp.role_id}")
            duplicate_check[selected_role_id_str] = rp.priority

        player_with_roles = await self._player_repo.get(player.id, load_roles=True)
        existing_roles = player_with_roles.player_roles if player_with_roles else []

        new_role_ids = {role_id_map[rp.role_id] for rp in command.role_priorities}

        for existing_role in existing_roles:
            if existing_role.game_role_id not in new_role_ids:
                await self._player_role_repo.delete(existing_role.id)

        for rp in command.role_priorities:
            selected_role_id = role_id_map[rp.role_id]
            existing = next(
                (r for r in existing_roles if r.game_role_id == selected_role_id),
                None,
            )
            if existing:
                if existing.priority != rp.priority:
                    await self._player_role_repo.update(
                        PlayerRoleUpdate(id=existing.id, priority=rp.priority)
                    )
            else:
                await self._player_role_repo.create(
                    PlayerRoleCreate(
                        game_role_id=selected_role_id,
                        priority=rp.priority,
                        event_player_id=player.id,
                    )
                )

        updated = await self._player_repo.get(player.id, load_roles=True)
        return PlayerRolesUpdateResult(
            player_id=player.id,
            roles=[
                PlayerRoleItem(id=r.id, game_role_id=r.game_role_id, priority=r.priority)
                for r in (updated.player_roles if updated else [])
            ],
        )

    async def get_bulk(self, command: GetBulkPlayersCommand) -> list[PlayerItem]:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can list players")

        players = await self._player_repo.list_by_ids(command.event_id, command.player_ids)
        return [PlayerItem.model_validate(p) for p in players]

    async def remove(self, command: RemovePlayerCommand) -> None:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data
        if not is_same_server(access, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_event_admin_permission(access, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can remove players")

        if event.status == EventStatus.CANCELLED:
            raise BadRequestException("Cannot remove players from a cancelled event")

        player = await self._player_repo.get_by_event_and_member(command.event_id, command.member_id)
        if not player:
            raise NotFoundException("EventPlayer not found")

        if player.status == EventPlayerStatus.PLAYING:
            raise BadRequestException(
                "Cannot remove a player currently in an active match"
            )

        await self._player_repo.delete(player.id)
