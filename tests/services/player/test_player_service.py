from uuid import uuid4

import pytest

from src.core.commands.player import ListPlayersCommand, UpdatePlayerStatusCommand
from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.models.event_player import EventPlayerStatus
from src.core.services.player import PlayerService
from tests.services.helpers import InMemoryEventRepository, make_access, make_event

pytestmark = pytest.mark.asyncio


class MissingEventRepository:
    async def get(self, *_args, **_kwargs):
        return None


def make_service(event_repo):
    return PlayerService(event_repo=event_repo, player_repo=object())


async def test_get_list_raises_not_found_when_event_is_missing():
    service = make_service(MissingEventRepository())

    with pytest.raises(NotFoundException):
        await service.get_list(ListPlayersCommand(event_id=uuid4(), access_data=make_access()))


async def test_update_status_rejects_different_server():
    event = make_event(server_id=uuid4(), organizer_member_ids=[uuid4()])
    service = make_service(InMemoryEventRepository([event]))

    with pytest.raises(ForbiddenException):
        await service.update_status(
            UpdatePlayerStatusCommand(
                event_id=event.id,
                member_id=uuid4(),
                status=EventPlayerStatus.REGISTERED,
                access_data=make_access(server_id=uuid4()),
            )
        )
