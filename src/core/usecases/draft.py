from uuid import UUID

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.exceptions import ForbiddenException, NotFoundException, ConflictException, BadRequestException
from src.core.models.draft import Draft, DraftCreate
from src.core.models.drafted_player import DraftedPlayerCreate
from src.core.models.event import EventStatus, EventMatchType
from src.core.models.event_player import EventPlayerStatus, EventPlayerUpdate
from src.core.results.event import EventCard
from src.core.usecases._access import (
    P_EVENT_ADMIN_MANAGE_PLAYERS,
    has_event_admin_permission,
    has_server_ban,
    is_same_server,
)


class CreateDraftUseCase:
    def __init__(self, event_repo, organizer_repo, player_repo, draft_repo, drafted_player_repo, match_repo):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._player_repo = player_repo
        self._draft_repo = draft_repo
        self._drafted_player_repo = drafted_player_repo
        self._match_repo = match_repo

    async def __call__(self, cmd: CreateDraftCommand) -> Draft:
        event = await self._event_repo.get(
            cmd.event_id,
            load_organizers=True,
            load_integrations=False,
            load_time_settings=False,
            load_game_roles=False,
            load_custom_fields=False,
            load_applications=False,
            load_teams=False,
            load_drafts=False,
            load_players=False,
            load_brackets=False,
        )
        if event is None:
            raise NotFoundException(f"Event {cmd.event_id} not found")

        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can create draft")

        if has_server_ban(cmd.access_data):
            raise ForbiddenException("Server ban restriction applies")

        if event.status not in (EventStatus.REGISTRATION, EventStatus.IDLE, EventStatus.IN_PROGRESS):
            raise BadRequestException("Event is not in a state that allows draft creation")

        if cmd.player_ids:
            players = []
            for pid in cmd.player_ids:
                p = await self._player_repo.get(pid, load_roles=False, load_drafted=False)
                if p is None or p.event_id != cmd.event_id:
                    raise NotFoundException(f"Player {pid} not found in event {cmd.event_id}")
                allowed_statuses = {EventPlayerStatus.REGISTERED, EventPlayerStatus.BENCHED}
                if event.allow_multiple_drafts:
                    allowed_statuses.add(EventPlayerStatus.SELECTED)
                if p.status not in allowed_statuses:
                    raise BadRequestException(f"Player {pid} has status {p.status}, cannot be drafted")
                players.append(p)
        else:
            statuses = cmd.statuses or [EventPlayerStatus.REGISTERED, EventPlayerStatus.BENCHED]
            players = []
            per_status_limit = cmd.limit or 1000
            for status in statuses:
                players.extend(await self._player_repo.list_by_event(cmd.event_id, 0, per_status_limit, status=status))
            if cmd.pinned_only:
                players = [p for p in players if p.is_draft_pinned]

        busy_ids = await self._resolve_busy_players(cmd.event_id, event.allow_multiple_drafts)
        available = [p for p in players if p.id not in busy_ids]
        if cmd.limit is not None:
            available = available[:cmd.limit]

        if not available:
            raise ConflictException("No eligible players available for draft")

        draft = await self._draft_repo.create(DraftCreate(event_id=cmd.event_id))

        for player in available:
            await self._drafted_player_repo.create(
                DraftedPlayerCreate(draft_id=draft.id, event_player_id=player.id)
            )
            await self._player_repo.update(player.id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))

        result = await self._draft_repo.get(draft.id, load_drafted_players=True)
        if result is None:
            raise NotFoundException("Draft not found after creation")
        return result

    async def _resolve_busy_players(self, event_id: UUID, allow_multiple: bool) -> set[UUID]:
        if allow_multiple:
            return set()

        busy_draft_ids = await self._match_repo.list_active_draft_ids_by_event(event_id)
        busy_ids: set[UUID] = set()
        for did in busy_draft_ids:
            drafted = await self._draft_repo.get(did, load_drafted_players=True)
            if drafted:
                for dp in drafted.drafted_players:
                    busy_ids.add(dp.event_player_id)
        return busy_ids


class GetDraftUseCase:
    def __init__(self, draft_repo, event_repo, organizer_repo):
        self._draft_repo = draft_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, cmd: GetDraftCommand) -> Draft:
        draft = await self._draft_repo.get(cmd.draft_id, load_drafted_players=True)
        if draft is None:
            raise NotFoundException(f"Draft {cmd.draft_id} not found")

        if cmd.access_data is not None:
            event = await self._event_repo.get(
                draft.event_id,
                load_organizers=True,
                load_integrations=False,
                load_time_settings=False,
                load_game_roles=False,
                load_custom_fields=False,
                load_applications=False,
                load_teams=False,
                load_drafts=False,
                load_players=False,
                load_brackets=False,
            )
            if event is None:
                raise NotFoundException(f"Event {draft.event_id} not found")
            if not is_same_server(cmd.access_data, event.server_id):
                raise ForbiddenException("Event belongs to a different server")
            is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
            is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
            if not is_organizer and not is_admin:
                raise ForbiddenException("Access denied")

        return draft


class ListDraftsUseCase:
    def __init__(self, draft_repo, event_repo, organizer_repo):
        self._draft_repo = draft_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    async def __call__(self, cmd: ListDraftsCommand) -> list[Draft]:
        if cmd.access_data is not None:
            event = await self._event_repo.get(
                cmd.event_id,
                load_organizers=True,
                load_integrations=False,
                load_time_settings=False,
                load_game_roles=False,
                load_custom_fields=False,
                load_applications=False,
                load_teams=False,
                load_drafts=False,
                load_players=False,
                load_brackets=False,
            )
            if event is None:
                raise NotFoundException(f"Event {cmd.event_id} not found")
            if not is_same_server(cmd.access_data, event.server_id):
                raise ForbiddenException("Event belongs to a different server")
            is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
            is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_PLAYERS)
            if not is_organizer and not is_admin:
                raise ForbiddenException("Access denied")

        result = await self._draft_repo.list_by_event(
            cmd.event_id,
            (cmd.pagination.page - 1) * cmd.pagination.page_size if cmd.pagination.page else 0,
            cmd.pagination.page_size,
        )
        return list(result)
