from uuid import uuid4

import pytest

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.exceptions import NotFoundException
from src.core.services.draft import DraftService
from tests.services.helpers import make_access

pytestmark = pytest.mark.asyncio


class MissingEventRepository:
    async def get(self, *_args, **_kwargs):
        return None


class MissingDraftRepository:
    async def get(self, *_args, **_kwargs):
        return None


def make_service(*, event_repo=None, draft_repo=None):
    return DraftService(
        event_repo=event_repo or MissingEventRepository(),
        organizer_repo=object(),
        player_repo=object(),
        draft_repo=draft_repo or MissingDraftRepository(),
        drafted_player_repo=object(),
        match_repo=object(),
    )


async def test_create_raises_not_found_when_event_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.create(CreateDraftCommand(event_id=uuid4(), access_data=make_access()))


async def test_get_raises_not_found_when_draft_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.get(GetDraftCommand(draft_id=uuid4(), access_data=make_access()))


async def test_get_list_raises_not_found_when_event_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.get_list(ListDraftsCommand(event_id=uuid4(), access_data=make_access()))
