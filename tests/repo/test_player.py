"""
Test suite for PlayerRepository using testcontainers + pytest.
Tests CRUD operations, relationship loading, status filtering, and edge cases.
"""
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import NotFoundException
from src.core.models.event_player import EventPlayer, EventPlayerCreate, EventPlayerUpdate, EventPlayerStatus
from src.core.models.event import EventCreate, EventMatchType, EventStatus, TeamFormation
from src.infra.postgre.repo.player import PlayerRepository
from src.infra.postgre.repo.event import EventRepository


@pytest.fixture
def server_id() -> UUID:
    """Fixture providing a unique server ID per test."""
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    """Fixture providing a created event for player association."""
    event_repo = EventRepository(async_session)
    return await event_repo.create(
        EventCreate(
            server_id=server_id,
            name="Player Test Event",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
            status=EventStatus.CREATED
        )
    )


@pytest.fixture
def player_repo(async_session):
    """Fixture providing PlayerRepository instance."""
    return PlayerRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    """Fixture providing EventRepository instance."""
    return EventRepository(async_session)


class TestPlayerRepository:
    """Test suite for PlayerRepository (EventPlayer) operations."""

    async def test_create_player(self, player_repo, event_dto):
        """
        Test: Creating an event player successfully.
        When: EventPlayerCreate DTO is passed with valid event_id and member_id.
        Then: EventPlayer is created and returned with correct attributes.
        """
        # Arrange
        member_id = uuid4()
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=member_id
        )

        # Act
        created_player = await player_repo.create(player_create)

        # Assert
        assert created_player.id is not None
        assert created_player.event_id == event_dto.id
        assert created_player.member_id == member_id
        assert created_player.is_draft_pinned is False
        assert isinstance(created_player, EventPlayer)

    async def test_create_player_foreign_key_violation(self, player_repo):
        """
        Test: Creating player with non-existent event_id raises exception.
        When: EventPlayerCreate uses random UUID for event_id.
        Then: IntegrityForeignException is raised on flush.
        """
        # Arrange
        player_create = EventPlayerCreate(
            event_id=uuid4(),  # Non-existent event
            member_id=uuid4()
        )

        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await player_repo.create(player_create)

    async def test_get_player_by_id(self, player_repo, event_dto):
        """
        Test: Retrieving player by ID.
        When: Valid player ID is passed.
        Then: Player is returned with matching attributes.
        """
        # Arrange
        member_id = uuid4()
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=member_id
        )
        created = await player_repo.create(player_create)

        # Act
        retrieved = await player_repo.get(created.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id
        assert retrieved.member_id == member_id

    async def test_get_non_existent_player_returns_none(self, player_repo):
        """
        Test: Retrieving non-existent player returns None.
        When: Random UUID is passed as player_id.
        Then: None is returned instead of raising exception.
        """
        # Act
        result = await player_repo.get(uuid4())

        # Assert
        assert result is None

    async def test_get_player_with_roles_relation(self, player_repo, event_dto):
        """
        Test: Loading player with related roles.
        When: load_roles=True flag is passed.
        Then: Player is returned and player_roles list is populated (empty initially).
        """
        # Arrange
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await player_repo.create(player_create)

        # Act
        retrieved = await player_repo.get(created.id, load_roles=True)

        # Assert
        assert retrieved is not None
        assert hasattr(retrieved, 'player_roles')
        assert retrieved.player_roles == []

    async def test_get_player_with_drafted_relation(self, player_repo, event_dto):
        """
        Test: Loading player with related drafted players.
        When: load_drafted=True flag is passed.
        Then: Player is returned and drafted_players list is populated.
        """
        # Arrange
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await player_repo.create(player_create)

        # Act
        retrieved = await player_repo.get(created.id, load_drafted=True)

        # Assert
        assert retrieved is not None
        assert hasattr(retrieved, 'drafted_players')
        assert retrieved.drafted_players == []

    async def test_get_by_event_and_member(self, player_repo, event_dto):
        """
        Test: Retrieving player by event_id and member_id combination.
        When: Valid event_id and member_id are provided.
        Then: Player is returned or None if no match.
        """
        # Arrange
        member_id = uuid4()
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=member_id
        )
        created = await player_repo.create(player_create)

        # Act
        retrieved = await player_repo.get_by_event_and_member(event_dto.id, member_id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.member_id == member_id

    async def test_get_by_event_and_member_not_found(self, player_repo, event_dto):
        """
        Test: get_by_event_and_member returns None for non-matching member.
        When: Valid event_id but non-matching member_id.
        Then: None is returned.
        """
        # Act
        result = await player_repo.get_by_event_and_member(event_dto.id, uuid4())

        # Assert
        assert result is None

    async def test_get_by_event_and_member_wrong_event(self, player_repo, event_dto):
        """
        Test: get_by_event_and_member returns None for wrong event.
        When: Valid member_id but event_id is incorrect.
        Then: None is returned.
        """
        # Arrange
        member_id = uuid4()
        await player_repo.create(EventPlayerCreate(
            event_id=event_dto.id,
            member_id=member_id
        ))

        # Act
        result = await player_repo.get_by_event_and_member(uuid4(), member_id)

        # Assert
        assert result is None

    async def test_list_by_event(self, player_repo, event_dto):
        """
        Test: Listing all players for a specific event.
        When: Multiple players are created for the same event.
        Then: list_by_event returns all of them.
        """
        # Arrange
        member_1 = uuid4()
        member_2 = uuid4()
        member_3 = uuid4()

        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_1))
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_2))
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_3))

        # Act
        players = await player_repo.list_by_event(event_dto.id)

        # Assert
        assert len(players) == 3
        assert all(p.event_id == event_dto.id for p in players)

    async def test_list_by_event_filter_by_status(self, player_repo, event_dto):
        """
        Test: Filtering players by status.
        When: list_by_event is called with status filter.
        Then: Only players with matching status are returned.
        """
        # Arrange
        player1 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid4()))
        player2 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid4()))
        player3 = await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=uuid4()))

        # Update some players to SELECTED status
        await player_repo.update(player1.id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))
        await player_repo.update(player3.id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))
        # player2 remains REGISTERED

        # Act
        selected_players = await player_repo.list_by_event(event_dto.id, status=EventPlayerStatus.SELECTED)
        registered_players = await player_repo.list_by_event(event_dto.id, status=EventPlayerStatus.REGISTERED)

        # Assert
        assert len(selected_players) == 2
        assert len(registered_players) == 1
        assert all(p.status == EventPlayerStatus.SELECTED for p in selected_players)
        assert all(p.status == EventPlayerStatus.REGISTERED for p in registered_players)

    async def test_list_by_event_with_pagination(self, player_repo, event_dto):
        """
        Test: Listing players with pagination.
        When: Multiple players exist and offset/limit are specified.
        Then: Returned list respects pagination boundaries.
        """
        # Arrange
        for i in range(5):
            await player_repo.create(
                EventPlayerCreate(event_id=event_dto.id, member_id=uuid4())
            )

        # Act
        page_1 = await player_repo.list_by_event(event_dto.id, offset=0, limit=2)
        page_2 = await player_repo.list_by_event(event_dto.id, offset=2, limit=2)
        page_3 = await player_repo.list_by_event(event_dto.id, offset=4, limit=2)

        # Assert
        assert len(page_1) == 2
        assert len(page_2) == 2
        assert len(page_3) == 1

    async def test_list_by_event_empty_when_no_players(self, player_repo, event_dto):
        """
        Test: Listing players for event with no players returns empty list.
        When: list_by_event is called for an event with zero players.
        Then: Empty list is returned.
        """
        # Act
        players = await player_repo.list_by_event(event_dto.id)

        # Assert
        assert len(players) == 0

    async def test_list_by_event_with_roles(self, player_repo, event_dto):
        """
        Test: Listing players with roles relationship loaded.
        When: list_by_event_with_roles is called.
        Then: Players are returned with player_roles populated.
        """
        # Arrange
        member_1 = uuid4()
        member_2 = uuid4()
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_1))
        await player_repo.create(EventPlayerCreate(event_id=event_dto.id, member_id=member_2))

        # Act
        players_with_roles = await player_repo.list_by_event_with_roles(event_dto.id)

        # Assert
        assert len(players_with_roles) == 2
        assert all(hasattr(p, 'player_roles') for p in players_with_roles)

    async def test_update_player(self, player_repo, event_dto):
        """
        Test: Updating player status.
        When: update is called with EventPlayerUpdate DTO.
        Then: Player is updated and returned with new values.
        """
        # Arrange
        member_id = uuid4()
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=member_id
        )
        created = await player_repo.create(player_create)

        player_update = EventPlayerUpdate(is_draft_pinned=True)

        # Act
        updated = await player_repo.update(created.id, player_update)

        # Assert
        assert updated.id == created.id
        assert updated.is_draft_pinned is True
        assert updated.event_id == event_dto.id
        assert updated.member_id == member_id

    async def test_update_player_not_found(self, player_repo):
        """
        Test: Updating non-existent player raises NotFoundException.
        When: update is called with invalid player_id.
        Then: NotFoundException is raised.
        """
        # Arrange
        player_update = EventPlayerUpdate(is_draft_pinned=True)
        invalid_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            await player_repo.update(invalid_id, player_update)

    async def test_delete_player(self, player_repo, event_dto):
        """
        Test: Deleting a player.
        When: delete is called with valid player_id.
        Then: Player is removed and subsequent get returns None.
        """
        # Arrange
        player_create = EventPlayerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await player_repo.create(player_create)

        # Act
        delete_result = await player_repo.delete(created.id)

        # Assert
        assert delete_result is True
        retrieved_after_delete = await player_repo.get(created.id)
        assert retrieved_after_delete is None

    async def test_delete_non_existent_player_returns_false(self, player_repo):
        """
        Test: Deleting non-existent player returns False.
        When: delete is called with random UUID.
        Then: False is returned (no exception).
        """
        # Act
        result = await player_repo.delete(uuid4())

        # Assert
        assert result is False

    async def test_list_players_different_events_isolated(self, player_repo, event_repo, server_id):
        """
        Test: Players from different events are isolated.
        When: Multiple events have players.
        Then: list_by_event returns only players for that specific event.
        """
        # Arrange
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
                status=EventStatus.CREATED
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
                status=EventStatus.CREATED
            )
        )

        await player_repo.create(EventPlayerCreate(event_id=event1.id, member_id=uuid4()))
        await player_repo.create(EventPlayerCreate(event_id=event2.id, member_id=uuid4()))

        # Act
        event1_players = await player_repo.list_by_event(event1.id)
        event2_players = await player_repo.list_by_event(event2.id)

        # Assert
        assert len(event1_players) == 1
        assert len(event2_players) == 1
        assert event1_players[0].event_id == event1.id
        assert event2_players[0].event_id == event2.id




