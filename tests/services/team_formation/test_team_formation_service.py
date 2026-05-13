from uuid import uuid4

import pytest

from src.core.commands.team_formation import GetTeamFormationCommand, RunTeamFormationCommand
from src.core.exceptions import NotFoundException
from src.core.services.team_formation import TeamFormationService
from tests.services.helpers import InMemoryDraftRepository, InMemoryEventRepository, make_access, make_draft, make_event

pytestmark = pytest.mark.asyncio


class MissingDraftRepository:
    async def get(self, *_args, **_kwargs):
        return None


class EmptyVariantStore:
    async def get_latest_by_draft(self, *_args, **_kwargs):
        return None


class EnvStub:
    team_formation_variants_ttl_seconds = 3600


def make_service(*, event_repo=None, draft_repo=None, variant_store=None):
    return TeamFormationService(
        event_repo=event_repo or InMemoryEventRepository([]),
        organizer_repo=object(),
        draft_repo=draft_repo or MissingDraftRepository(),
        player_repo=object(),
        team_repo=object(),
        team_player_repo=object(),
        variant_store=variant_store or EmptyVariantStore(),
        rating_client=object(),
        mix_balancer_client=object(),
        tournament_balancer_client=object(),
        env=EnvStub(),
    )


async def test_run_raises_not_found_when_draft_is_missing():
    service = make_service()

    with pytest.raises(NotFoundException):
        await service.run(RunTeamFormationCommand(draft_id=uuid4(), access_data=make_access()))


async def test_get_raises_not_found_when_cached_job_is_missing():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id])
    draft = make_draft(event.id)
    service = make_service(
        event_repo=InMemoryEventRepository([event]),
        draft_repo=InMemoryDraftRepository([draft]),
        variant_store=EmptyVariantStore(),
    )

    with pytest.raises(NotFoundException):
        await service.get(
            GetTeamFormationCommand(
                draft_id=draft.id,
                access_data=make_access(server_id=server_id, member_id=organizer_id),
            )
        )
