from uuid import uuid4

import pytest

from src.core.commands.match import RecordMatchResultCommand, SetupMatchCommand
from src.core.exceptions import NotFoundException
from src.core.services.match import MatchService
from tests.services.helpers import make_access

pytestmark = pytest.mark.asyncio


class MissingEventRepository:
    async def get(self, *_args, **_kwargs):
        return None


class MissingMatchRepository:
    async def get_event_context(self, *_args, **_kwargs):
        return None


class EnvStub:
    rating_match_process_enabled = False


def make_service(*, event_repo=None, match_repo=None):
    return MatchService(
        event_repo=event_repo or MissingEventRepository(),
        bracket_repo=object(),
        stage_repo=object(),
        stage_group_repo=object(),
        match_repo=match_repo or MissingMatchRepository(),
        match_slot_repo=object(),
        match_score_repo=object(),
        team_repo=object(),
        draft_repo=object(),
        player_repo=object(),
        rating_client=object(),
        env=EnvStub(),
    )


async def test_setup_raises_not_found_when_event_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.setup(
            SetupMatchCommand(event_id=uuid4(), team_ids=[uuid4(), uuid4()], access_data=make_access())
        )


async def test_record_result_raises_not_found_when_match_context_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.record_result(
            RecordMatchResultCommand(match_id=uuid4(), scores={}, access_data=make_access())
        )
