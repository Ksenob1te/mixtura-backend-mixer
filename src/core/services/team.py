from src.core.commands.team import ListTeamsCommand
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.team import TeamRepositoryProtocol
from src.core.models.team import Team
from src.core.interfaces.repo.access import (
    P_EVENT_ADMIN_MANAGE_BRACKET,
    has_event_admin_permission,
    is_same_server,
)


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepositoryProtocol,
        event_repo: EventRepositoryProtocol,
    ):
        self._team_repo = team_repo
        self._event_repo = event_repo

    async def list(self, cmd: ListTeamsCommand) -> list[Team]:
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
        has_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not has_admin:
            raise ForbiddenException("Access denied")

        result = await self._team_repo.list_by_event(
            cmd.event_id,
            (cmd.pagination.page - 1) * cmd.pagination.page_size if cmd.pagination.page else 0,
            cmd.pagination.page_size,
        )
        return list(result)
