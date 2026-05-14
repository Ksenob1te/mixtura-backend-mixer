from uuid import uuid4

import pytest

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus
from src.core.models.event_player import EventPlayerCreate, EventPlayerStatus

pytestmark = pytest.mark.asyncio


class TestDraftService:
    async def test_create_selects_requested_players(self, draft_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        # create event and add organizer
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        player_one = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False))
        player_two = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), is_draft_pinned=False, status=EventPlayerStatus.BENCHED))

        result = await draft_service.create(
            CreateDraftCommand(
                event_id=event.id,
                player_ids=[player_one.id, player_two.id],
                access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
            )
        )

        assert result.event_id == event.id
        assert [drafted.event_player_id for drafted in result.drafted_players] == [player_one.id, player_two.id]
        assert (await player_repo.get(player_one.id)).status == EventPlayerStatus.SELECTED
        assert (await player_repo.get(player_two.id)).status == EventPlayerStatus.SELECTED

    async def test_create_raises_not_found_when_event_is_missing(self, draft_service):
        with pytest.raises(NotFoundException):
            await draft_service.create(CreateDraftCommand(event_id=uuid4(), access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_get_raises_not_found_when_draft_is_missing(self, draft_service):
        with pytest.raises(NotFoundException):
            await draft_service.get(GetDraftCommand(draft_id=uuid4(), access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_get_list_returns_event_drafts(self, draft_service, event_repo, server_id, organizer_id, draft_repo, organizer_repo):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        draft_one = await draft_repo.create(dict(event_id=event.id))
        draft_two = await draft_repo.create(dict(event_id=event.id))

        result = await draft_service.get_list(
            ListDraftsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id))
        )

        assert [draft.id for draft in result] == [draft_one.id, draft_two.id]

    async def test_create_rejects_non_organizer_without_admin(self, draft_service, event_repo, player_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await draft_service.create(
                CreateDraftCommand(
                    event_id=event.id,
                    player_ids=[player.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=uuid4()),
                )
            )

    async def test_create_rejects_event_status_not_allowed(self, draft_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CANCELLED, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        with pytest.raises(BadRequestException):
            await draft_service.create(
                CreateDraftCommand(
                    event_id=event.id,
                    player_ids=[player.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_create_rejects_when_no_eligible_players(self, draft_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), status=EventPlayerStatus.PLAYING))

        with pytest.raises(BadRequestException):
            await draft_service.create(
                CreateDraftCommand(
                    event_id=event.id,
                    player_ids=[player.id],
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_create_rejects_empty_auto_selection(self, draft_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=False, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(ConflictException):
            await draft_service.create(
                CreateDraftCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

