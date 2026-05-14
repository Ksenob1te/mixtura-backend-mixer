from uuid import uuid4

import pytest

from src.core.commands.team import ListTeamsCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_MANAGE_BRACKET
from src.core.models.event import EventCreate, EventMatchType, EventStatus
from src.core.models.team import TeamCreate

pytestmark = pytest.mark.asyncio


class TestTeamService:
    async def test_get_list_raises_not_found_when_event_is_missing(self, team_service):
        with pytest.raises(NotFoundException):
            await team_service.get_list(ListTeamsCommand(event_id=uuid4(), access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_get_list_returns_teams_for_organizer(self, team_service, event_repo, organizer_repo, team_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        team_one = await team_repo.create(TeamCreate(event_id=event.id, name="Alpha"))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, name="Beta"))

        result = await team_service.get_list(ListTeamsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert [team.id for team in result] == [team_one.id, team_two.id]

    async def test_get_list_rejects_non_organizer_without_admin_permission(self, team_service, event_repo, organizer_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await team_service.get_list(ListTeamsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id)))

    async def test_get_list_allows_event_admin_permission(self, team_service, event_repo, team_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        team = await team_repo.create(TeamCreate(event_id=event.id, name="Alpha"))

        result = await team_service.get_list(ListTeamsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, permission_mask=P_EVENT_ADMIN_MANAGE_BRACKET)))

        assert len(result) == 1

    async def test_get_list_rejects_different_server(self, team_service, event_repo, organizer_repo, team_repo, organizer_id):
        event_server = uuid4()
        event = await event_repo.create(EventCreate(server_id=event_server, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        await team_repo.create(TeamCreate(event_id=event.id, name="Alpha"))

        with pytest.raises(ForbiddenException):
            await team_service.get_list(
                ListTeamsCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=uuid4(), member_id=organizer_id),
                )
            )

