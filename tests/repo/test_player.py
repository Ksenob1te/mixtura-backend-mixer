import uuid
import pytest

from src.core.exceptions import NotFoundException
from src.core.models.event import Event, EventCreate, EventMatchType, EventStatus, TeamFormation
from src.core.models.event_player import (
    EventPlayer,
    EventPlayerCreate,
    EventPlayerStatus,
    EventPlayerUpdate,
)
from src.infra.postgre.exceptions import IntegrityForeignException
from src.infra.postgre.repo.player import PlayerRepository

pytestmark = pytest.mark.asyncio


class TestPlayerRepository:
    async def test_create_player(self, player_repo: PlayerRepository, event_dto: Event):
        member_id = uuid.uuid4()
        created_player = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=member_id)
        )

        assert isinstance(created_player, EventPlayer)
        assert created_player.id is not None
        assert created_player.event_id == event_dto.id
        assert created_player.member_id == member_id
        assert created_player.is_draft_pinned is False

    async def test_create_player_foreign_key_violation(self, player_repo: PlayerRepository):
        with pytest.raises(IntegrityForeignException):
            await player_repo.create(
                EventPlayerCreate(event_id=uuid.uuid4(), member_id=uuid.uuid4())
            )

    async def test_get_player_by_id(self, player_repo: PlayerRepository, event_dto: Event):
        member_id = uuid.uuid4()
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=member_id)
        )
        retrieved = await player_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id
        assert retrieved.member_id == member_id

    async def test_get_non_existent_player_returns_none(self, player_repo: PlayerRepository):
        assert await player_repo.get(uuid.uuid4()) is None

    async def test_get_player_with_roles_relation(self, player_repo: PlayerRepository, event_dto: Event):
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )
        retrieved = await player_repo.get(created.id, load_roles=True)

        assert retrieved is not None
        assert hasattr(retrieved, "player_roles")
        assert retrieved.player_roles == []

    async def test_get_player_with_drafted_relation(self, player_repo: PlayerRepository, event_dto: Event):
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )
        retrieved = await player_repo.get(created.id, load_drafted=True)

        assert retrieved is not None
        assert hasattr(retrieved, "drafted_players")
        assert retrieved.drafted_players == []

    async def test_get_by_event_and_member(self, player_repo: PlayerRepository, event_dto: Event):
        member_id = uuid.uuid4()
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=member_id)
        )
        retrieved = await player_repo.get_by_event_and_member(event_dto.id, member_id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.member_id == member_id

    async def test_get_by_event_and_member_not_found(self, player_repo: PlayerRepository, event_dto: Event):
        assert await player_repo.get_by_event_and_member(event_dto.id, uuid.uuid4()) is None

    async def test_get_by_event_and_member_wrong_event(self, player_repo: PlayerRepository, event_dto: Event):
        member_id = uuid.uuid4()
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_id))

        assert await player_repo.get_by_event_and_member(uuid.uuid4(), member_id) is None

    async def test_list_by_event(self, player_repo: PlayerRepository, event_dto: Event):
        for _ in range(3):
            await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))

        players = await player_repo.list_by_event(event_dto.id)

        assert len(players) == 3
        assert all(player.event_id == event_dto.id for player in players)

    async def test_list_by_event_filter_by_status(self, player_repo: PlayerRepository, event_dto: Event):
        player1 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))
        player2 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))
        player3 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))

        await player_repo.update(player1.id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))
        await player_repo.update(player3.id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))

        selected_players = await player_repo.list_by_event(event_dto.id, status=EventPlayerStatus.SELECTED)
        registered_players = await player_repo.list_by_event(event_dto.id, status=EventPlayerStatus.REGISTERED)

        assert len(selected_players) == 2
        assert len(registered_players) == 1
        assert all(player.status == EventPlayerStatus.SELECTED for player in selected_players)
        assert all(player.status == EventPlayerStatus.REGISTERED for player in registered_players)

    async def test_list_by_event_with_pagination(self, player_repo: PlayerRepository, event_dto: Event):
        for _ in range(5):
            await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))

        assert len(await player_repo.list_by_event(event_dto.id, offset=0, limit=2)) == 2
        assert len(await player_repo.list_by_event(event_dto.id, offset=2, limit=2)) == 2
        assert len(await player_repo.list_by_event(event_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_event_empty_when_no_players(self, player_repo: PlayerRepository, event_dto: Event):
        assert await player_repo.list_by_event(event_dto.id) == []

    async def test_list_by_event_with_roles(self, player_repo: PlayerRepository, event_dto: Event):
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))

        players_with_roles = await player_repo.list_by_event_with_roles(event_dto.id)

        assert len(players_with_roles) == 2
        assert all(hasattr(player, "player_roles") for player in players_with_roles)

    async def test_update_player(self, player_repo: PlayerRepository, event_dto: Event):
        member_id = uuid.uuid4()
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=member_id)
        )

        updated = await player_repo.update(created.id, EventPlayerUpdate(is_draft_pinned=True))

        assert updated.id == created.id
        assert updated.is_draft_pinned is True
        assert updated.event_id == event_dto.id
        assert updated.member_id == member_id

    async def test_update_player_not_found(self, player_repo: PlayerRepository):
        with pytest.raises(NotFoundException):
            await player_repo.update(uuid.uuid4(), EventPlayerUpdate(is_draft_pinned=True))

    async def test_delete_player(self, player_repo: PlayerRepository, event_dto: Event):
        created = await player_repo.create(
            EventPlayerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )

        assert await player_repo.delete(created.id) is True
        assert await player_repo.get(created.id) is None

    async def test_delete_non_existent_player_returns_false(self, player_repo: PlayerRepository):
        assert await player_repo.delete(uuid.uuid4()) is False

    async def test_list_players_different_events_isolated(
        self,
        player_repo: PlayerRepository,
        event_repo,
        server_id,
    ):
        event1 = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event 1",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                status=EventStatus.CREATED,
            )
        )
        event2 = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event 2",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                status=EventStatus.CREATED,
            )
        )

        await player_repo.create(EventPlayerCreate(event_id=event1.id, member_id=uuid.uuid4()))
        await player_repo.create(EventPlayerCreate(event_id=event2.id, member_id=uuid.uuid4()))

        event1_players = await player_repo.list_by_event(event1.id)
        event2_players = await player_repo.list_by_event(event2.id)

        assert len(event1_players) == 1
        assert len(event2_players) == 1
        assert event1_players[0].event_id == event1.id
        assert event2_players[0].event_id == event2.id
