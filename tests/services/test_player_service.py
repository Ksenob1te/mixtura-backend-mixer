from uuid import uuid4

import pytest

from src.core.commands.player import ListPlayersCommand, RemovePlayerCommand, UpdatePlayerStatusCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus
from src.core.models.event_player import EventPlayerCreate, EventPlayerStatus

pytestmark = pytest.mark.asyncio


class TestPlayerService:
    async def test_get_list_raises_not_found_when_event_is_missing(self, player_service):
        with pytest.raises(NotFoundException):
            await player_service.get_list(ListPlayersCommand(event_id=uuid4(), access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4())))

    async def test_get_list_returns_players_for_organizer(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player_one = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))
        player_two = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), status=EventPlayerStatus.SELECTED))

        result = await player_service.get_list(ListPlayersCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert {item["id"] for item in result} == {str(player_one.id), str(player_two.id)}

    async def test_update_status_changes_player_status(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        result = await player_service.update_status(
            UpdatePlayerStatusCommand(
                event_id=event.id,
                member_id=player.member_id,
                status=EventPlayerStatus.SELECTED,
                access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
            )
        )

        assert result["member_id"] == str(player.member_id)
        assert result["status"] == EventPlayerStatus.SELECTED.value
        assert (await player_repo.get_by_event_and_member(event.id, player.member_id)).status == EventPlayerStatus.SELECTED

    async def test_update_status_rejects_different_server(self, player_service, event_repo, player_repo):
        event = await event_repo.create(EventCreate(server_id=uuid4(), name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await player_service.update_status(
                UpdatePlayerStatusCommand(
                    event_id=event.id,
                    member_id=player.member_id,
                    status=EventPlayerStatus.REGISTERED,
                    access_data=AccessDataRequest(server_id=uuid4(), member_id=uuid4()),
                )
            )

    async def test_remove_deletes_player(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        await player_service.remove(RemovePlayerCommand(event_id=event.id, member_id=player.member_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert await player_repo.get_by_event_and_member(event.id, player.member_id) is None

    async def test_get_list_rejects_non_organizer(self, player_service, event_repo, organizer_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await player_service.get_list(
                ListPlayersCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=uuid4()),
                )
            )

    async def test_update_status_rejects_cancelled_event(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CANCELLED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4()))

        with pytest.raises(BadRequestException):
            await player_service.update_status(
                UpdatePlayerStatusCommand(
                    event_id=event.id,
                    member_id=player.member_id,
                    status=EventPlayerStatus.SELECTED,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_update_status_rejects_changing_playing_player(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), status=EventPlayerStatus.PLAYING))

        with pytest.raises(BadRequestException):
            await player_service.update_status(
                UpdatePlayerStatusCommand(
                    event_id=event.id,
                    member_id=player.member_id,
                    status=EventPlayerStatus.REGISTERED,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_remove_rejects_playing_player(self, player_service, event_repo, organizer_repo, player_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        player = await player_repo.create(EventPlayerCreate(event_id=event.id, member_id=uuid4(), status=EventPlayerStatus.PLAYING))

        with pytest.raises(BadRequestException):
            await player_service.remove(
                RemovePlayerCommand(
                    event_id=event.id,
                    member_id=player.member_id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

