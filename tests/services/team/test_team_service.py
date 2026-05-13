from uuid import uuid4

import pytest

from src.core.commands.team import ListTeamsCommand
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.services.team import TeamService
from tests.services.helpers import InMemoryEventRepository, make_access, make_event

pytestmark = pytest.mark.asyncio


class MissingEventRepository:
    async def get(self, *_args, **_kwargs):
        return None


def make_service(event_repo):
    return TeamService(team_repo=object(), event_repo=event_repo)


async def test_get_list_raises_not_found_when_event_is_missing():
    service = make_service(MissingEventRepository())

    with pytest.raises(NotFoundException):
        await service.get_list(ListTeamsCommand(event_id=uuid4(), access_data=make_access()))


async def test_get_list_rejects_non_organizer_without_admin_permission():
    server_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[uuid4()])
    service = make_service(InMemoryEventRepository([event]))

    with pytest.raises(ForbiddenException):
        await service.get_list(ListTeamsCommand(event_id=event.id, access_data=make_access(server_id=server_id)))
