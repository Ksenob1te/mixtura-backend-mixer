from uuid import uuid4

import pytest

from src.core.commands.team_formation import ChooseTeamFormationVariantCommand, GetTeamFormationCommand, RunTeamFormationCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from src.core.models.draft import DraftStatus, DraftUpdate
from src.core.models.draft import DraftCreate
from src.core.models.event import EventCreate, EventMatchType, EventStatus, TeamFormation
from src.core.models.player_role import PlayerRoleCreate
from src.core.models.event_player import EventPlayerCreate, EventPlayerStatus

pytestmark = pytest.mark.asyncio


class TestTeamFormationService:
    async def test_run_raises_not_found_when_draft_is_missing(self, team_formation_service):
        with pytest.raises(NotFoundException):
            await team_formation_service.run(RunTeamFormationCommand(draft_id=uuid4(), access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_run_returns_pending_and_publishes_to_balancer(
        self,
        team_formation_service,
        event_repo,
        organizer_repo,
        draft_repo,
        drafted_player_repo,
        player_repo,
        player_role_repo,
        selected_game_role_repo,
        balancer_repo,
        server_id,
        organizer_id,
    ):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        role_one = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        role_two = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))

        player_one = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_one.id, priority=1, event_player_id=player_one.id))
        player_two = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_two.id, priority=1, event_player_id=player_two.id))

        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_one.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_two.id))

        result = await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        stored = await draft_repo.get(draft.id)
        assert result.status == "pending"
        assert stored is not None
        assert stored.status == DraftStatus.BALANCE_REQUESTED
        assert len(balancer_repo.mix_calls) == 1
        assert balancer_repo.mix_calls[0]["draft_id"] == draft.id

    async def test_run_saves_variants_after_completion(
        self,
        team_formation_service,
        event_repo,
        organizer_repo,
        draft_repo,
        drafted_player_repo,
        player_repo,
        player_role_repo,
        selected_game_role_repo,
        balancer_repo,
        variant_store,
        server_id,
        organizer_id,
    ):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        role_one = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        role_two = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))

        player_one = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_one.id, priority=1, event_player_id=player_one.id))
        player_two = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_two.id, priority=1, event_player_id=player_two.id))

        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_one.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_two.id))

        result = await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        assert result.status == "pending"
        assert len(result.variants) == 0

        raw_variants = [
            {
                "teams": [
                    {"name": "Team A", "member_ids": [player_one.member_id], "event_player_ids": [player_one.id], "game_role_ids": [role_one.id], "calculated_ratings": [1200.0]},
                    {"name": "Team B", "member_ids": [player_two.member_id], "event_player_ids": [player_two.id], "game_role_ids": [role_two.id], "calculated_ratings": [1100.0]},
                ],
                "quality_uniformity": 0.9,
                "quality_role_fairness": 0.8,
                "vq_uniformity": 0.7,
                "constraint_violations": 0,
            }
        ]
        await team_formation_service.complete_formation(result.job_id, raw_variants)

        completed = await variant_store.get_latest_by_draft(event.id, draft.id)
        assert completed is not None
        assert completed.status == "completed"
        assert len(completed.variants) == 1
        assert completed.job_id == result.job_id

    async def test_get_raises_not_found_when_cached_job_is_missing(self, team_formation_service, event_repo, organizer_repo, selected_game_role_repo, draft_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))

        with pytest.raises(NotFoundException):
            await team_formation_service.get(GetTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_choose_variant_creates_teams_and_selects_players(self, team_formation_service, event_repo, organizer_repo, draft_repo, drafted_player_repo, player_repo, player_role_repo, selected_game_role_repo, team_repo, team_player_repo, balancer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        role_one = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        role_two = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))

        player_one = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_one.id, priority=1, event_player_id=player_one.id))
        player_two = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role_two.id, priority=1, event_player_id=player_two.id))

        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_one.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player_two.id))

        run_result = await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        raw_variants = [
            {
                "teams": [
                    {"name": "Team A", "member_ids": [player_one.member_id], "event_player_ids": [player_one.id], "game_role_ids": [role_one.id], "calculated_ratings": [1200.0]},
                    {"name": "Team B", "member_ids": [player_two.member_id], "event_player_ids": [player_two.id], "game_role_ids": [role_two.id], "calculated_ratings": [1100.0]},
                ],
                "quality_uniformity": 0.9,
                "quality_role_fairness": 0.8,
                "vq_uniformity": 0.7,
                "constraint_violations": 0,
            }
        ]
        await team_formation_service.complete_formation(run_result.job_id, raw_variants)

        completed = await team_formation_service.get(GetTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        variant_id = completed.variants[0].id

        teams = await team_formation_service.choose_variant(ChooseTeamFormationVariantCommand(draft_id=draft.id, variant_id=variant_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        stored_draft = await draft_repo.get(draft.id)
        assert len(teams) == 2
        assert (await team_repo.list_by_event(event.id, 0, 100))
        assert stored_draft is not None
        assert stored_draft.status == DraftStatus.BALANCE_SELECTED
        assert (await player_repo.get(player_one.id)).status == EventPlayerStatus.SELECTED
        assert (await player_repo.get(player_two.id)).status == EventPlayerStatus.SELECTED

    async def test_run_rejects_non_organizer_without_admin(self, team_formation_service, event_repo, draft_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))

        with pytest.raises(ForbiddenException):
            await team_formation_service.run(
                RunTeamFormationCommand(
                    draft_id=draft.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=uuid4()),
                )
            )

    async def test_run_rejects_when_draft_not_open(self, team_formation_service, event_repo, organizer_repo, draft_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await draft_repo.update(DraftUpdate(id=draft.id, status=DraftStatus.BALANCE_REQUESTED))

        with pytest.raises(ConflictException):
            await team_formation_service.run(
                RunTeamFormationCommand(
                    draft_id=draft.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_choose_variant_rejects_missing_variant(self, team_formation_service, event_repo, organizer_repo, draft_repo, drafted_player_repo, player_repo, player_role_repo, selected_game_role_repo, balancer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        role = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role.id, priority=1, event_player_id=player.id))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player.id))

        run_result = await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        raw_variants = [
            {
                "teams": [
                    {"name": "A", "member_ids": [player.member_id], "event_player_ids": [player.id], "game_role_ids": [role.id], "calculated_ratings": [1200.0]}
                ],
                "quality_uniformity": 0.9,
                "quality_role_fairness": 0.8,
                "vq_uniformity": 0.7,
                "constraint_violations": 0,
            }
        ]
        await team_formation_service.complete_formation(run_result.job_id, raw_variants)

        with pytest.raises(NotFoundException):
            await team_formation_service.choose_variant(
                ChooseTeamFormationVariantCommand(
                    draft_id=draft.id,
                    variant_id=uuid4(),
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_choose_variant_rejects_pending_formation(self, team_formation_service, event_repo, organizer_repo, draft_repo, drafted_player_repo, player_repo, player_role_repo, selected_game_role_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        role = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role.id, priority=1, event_player_id=player.id))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player.id))

        await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        with pytest.raises(ConflictException, match="still in progress"):
            await team_formation_service.choose_variant(
                ChooseTeamFormationVariantCommand(
                    draft_id=draft.id,
                    variant_id=uuid4(),
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_get_returns_pending_job_after_run(
        self,
        team_formation_service,
        event_repo,
        organizer_repo,
        selected_game_role_repo,
        draft_repo,
        drafted_player_repo,
        player_repo,
        player_role_repo,
        server_id,
        organizer_id,
    ):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, team_formation=TeamFormation.BALANCE, use_application=False, is_public=True, team_size=2, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        role = await selected_game_role_repo.create(dict(event_id=event.id, game_role_id=uuid4()))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        await player_role_repo.create(PlayerRoleCreate(game_role_id=role.id, priority=1, event_player_id=player.id))
        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        await drafted_player_repo.create(dict(draft_id=draft.id, event_player_id=player.id))

        run_result = await team_formation_service.run(RunTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        assert run_result.status == "pending"

        job = await team_formation_service.get(GetTeamFormationCommand(draft_id=draft.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        assert job is not None
        assert job.status == "pending"
        assert job.job_id == run_result.job_id
