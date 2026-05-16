from src.core.commands.player import ListPlayersCommand, RemovePlayerCommand, UpdatePlayerStatusCommand
from src.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.models.event import EventStatus
from src.core.models.event_player import EventPlayerStatus, EventPlayerUpdate
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
    ):
        self._event_repo = event_repo
        self._player_repo = player_repo

    async def get_list(self, command: ListPlayersCommand) -> list[dict]:
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

        return [
            {
                "id": str(p.id),
                "member_id": str(p.member_id),
                "status": p.status.value,
                "is_draft_pinned": p.is_draft_pinned,
                "application_id": str(p.application_id) if p.application_id else None,
            }
            for p in players
        ]

    async def update_status(self, command: UpdatePlayerStatusCommand) -> dict:
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

        return {
            "id": str(player.id),
            "member_id": str(player.member_id),
            "status": player.status.value,
            "custom_id": str(player.custom_id) if player.custom_id else None,
        }

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
