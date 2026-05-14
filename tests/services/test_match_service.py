from uuid import uuid4

import pytest

from src.core.commands.match import RecordMatchResultCommand, SetupMatchCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus
from src.core.models.draft import DraftCreate
from src.core.models.team import TeamCreate
from src.core.models.team_player import TeamPlayerCreate
from src.core.models.match import MatchCreate
from src.core.models.match_slot import MatchSlotCreate, MatchSlotSourceType
from src.core.models.match_score import MatchScoreCreate
from src.core.models.stage import StageCreate, StageFormat
from src.core.models.stage_group import StageGroupCreate
from src.core.models.bracket import BracketCreate

pytestmark = pytest.mark.asyncio


class TestMatchService:
    async def test_setup_raises_not_found_when_event_is_missing(self, match_service):
        with pytest.raises(NotFoundException):
            await match_service.setup(SetupMatchCommand(event_id=uuid4(), team_ids=[uuid4(), uuid4()], access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_setup_creates_single_match_structure(self, match_service, event_repo, organizer_repo, draft_repo, team_repo, team_player_repo, match_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        draft = await draft_repo.create(DraftCreate(event_id=event.id))
        team_one = await team_repo.create(TeamCreate(event_id=event.id, draft_id=draft.id, name="Team A"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_one.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, draft_id=draft.id, name="Team B"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_two.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))

        result = await match_service.setup(
            SetupMatchCommand(event_id=event.id, team_ids=[team_one.id, team_two.id], access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id))
        )

        stored_match = await match_repo.get(result.match_id, load_slots=True)
        assert result.event_id == event.id
        assert result.draft_id == draft.id
        assert len(result.slots) == 2
        # bracket/stage/group created by service — assert match present
        assert stored_match is not None
        assert stored_match.group_id == result.group_id
        assert len(stored_match.slots) == 2

    async def test_record_result_raises_not_found_when_match_context_is_missing(self, match_service):
        with pytest.raises(NotFoundException):
            await match_service.record_result(RecordMatchResultCommand(match_id=uuid4(), scores={}, access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_setup_rejects_non_organizer_without_admin(self, match_service, event_repo, team_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        team_one = await team_repo.create(TeamCreate(event_id=event.id, name="A"))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, name="B"))

        with pytest.raises(ForbiddenException):
            await match_service.setup(
                SetupMatchCommand(
                    event_id=event.id,
                    team_ids=[team_one.id, team_two.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=uuid4()),
                )
            )

    async def test_setup_rejects_duplicate_team_ids(self, match_service, event_repo, organizer_repo, team_repo, team_player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        team = await team_repo.create(TeamCreate(event_id=event.id, name="A"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))

        with pytest.raises(BadRequestException):
            await match_service.setup(
                SetupMatchCommand(
                    event_id=event.id,
                    team_ids=[team.id, team.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_setup_rejects_event_status_not_allowed(self, match_service, event_repo, organizer_repo, team_repo, team_player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        team_one = await team_repo.create(TeamCreate(event_id=event.id, name="A"))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, name="B"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_one.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_two.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))

        with pytest.raises(ConflictException):
            await match_service.setup(
                SetupMatchCommand(
                    event_id=event.id,
                    team_ids=[team_one.id, team_two.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_record_result_updates_match_and_scores(self, match_service, event_repo, organizer_repo, bracket_repo, stage_repo, stage_group_repo, match_repo, match_slot_repo, match_score_repo, team_repo, team_player_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.IN_PROGRESS, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        team_one_member = uuid4()
        team_two_member = uuid4()
        await player_repo.create(dict(event_id=event.id, member_id=team_one_member))
        await player_repo.create(dict(event_id=event.id, member_id=team_two_member))
        team_one = await team_repo.create(TeamCreate(event_id=event.id, name="A"))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, name="B"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_one.id, member_id=team_one_member, game_role_id=uuid4(), rating=1000.0))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_two.id, member_id=team_two_member, game_role_id=uuid4(), rating=1000.0))

        bracket = await bracket_repo.create(BracketCreate(event_id=event.id))
        stage = await stage_repo.create(StageCreate(stage_index=1, bracket_id=bracket.id, format=StageFormat.SINGLE_MATCH, name="Single"))
        group = await stage_group_repo.create(StageGroupCreate(stage_id=stage.id, name="Group"))
        match = await match_repo.create(MatchCreate(group_id=group.id, match_index=1))
        slot_one = await match_slot_repo.create(MatchSlotCreate(match_id=match.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL))
        slot_two = await match_slot_repo.create(MatchSlotCreate(match_id=match.id, slot_num=2, source_type=MatchSlotSourceType.MANUAL))
        score_one = await match_score_repo.create(MatchScoreCreate(slot_id=slot_one.id, team_id=team_one.id, score=0))
        score_two = await match_score_repo.create(MatchScoreCreate(slot_id=slot_two.id, team_id=team_two.id, score=0))

        result = await match_service.record_result(
            RecordMatchResultCommand(
                match_id=match.id,
                scores={team_one.id: 2, team_two.id: 1},
                access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
            )
        )

        updated_match = await match_repo.get(match.id, load_slots=True)
        updated_score_one = await match_score_repo.get(score_one.id)
        updated_score_two = await match_score_repo.get(score_two.id)

        assert result.winner_team_id == team_one.id
        assert updated_match is not None
        assert updated_match.time_end is not None
        assert updated_score_one is not None and updated_score_one.score == 2
        assert updated_score_two is not None and updated_score_two.score == 1

    async def test_record_result_rejects_negative_score(self, match_service, event_repo, organizer_repo, bracket_repo, stage_repo, stage_group_repo, match_repo, match_slot_repo, match_score_repo, team_repo, team_player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.IN_PROGRESS, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=2, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        team_one = await team_repo.create(TeamCreate(event_id=event.id, name="A"))
        team_two = await team_repo.create(TeamCreate(event_id=event.id, name="B"))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_one.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))
        await team_player_repo.create(TeamPlayerCreate(team_id=team_two.id, member_id=uuid4(), game_role_id=uuid4(), rating=1000.0))
        bracket = await bracket_repo.create(BracketCreate(event_id=event.id))
        stage = await stage_repo.create(StageCreate(stage_index=1, bracket_id=bracket.id, format=StageFormat.SINGLE_MATCH, name="Single"))
        group = await stage_group_repo.create(StageGroupCreate(stage_id=stage.id, name="Group"))
        match = await match_repo.create(MatchCreate(group_id=group.id, match_index=1))
        slot_one = await match_slot_repo.create(MatchSlotCreate(match_id=match.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL))
        slot_two = await match_slot_repo.create(MatchSlotCreate(match_id=match.id, slot_num=2, source_type=MatchSlotSourceType.MANUAL))
        await match_score_repo.create(MatchScoreCreate(slot_id=slot_one.id, team_id=team_one.id, score=0))
        await match_score_repo.create(MatchScoreCreate(slot_id=slot_two.id, team_id=team_two.id, score=0))

        with pytest.raises(BadRequestException):
            await match_service.record_result(
                RecordMatchResultCommand(
                    match_id=match.id,
                    scores={team_one.id: -1, team_two.id: 1},
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

