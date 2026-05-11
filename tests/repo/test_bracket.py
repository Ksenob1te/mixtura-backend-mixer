from uuid import UUID, uuid4

import pytest

from src.core.models.bracket import Bracket, BracketCreate
from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.infra.postgre.repo.bracket import BracketRepository
from src.infra.postgre.repo.event import EventRepository


@pytest.fixture
def server_id() -> UUID:
    """Fixture providing a unique server ID per test."""
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    """Fixture providing a created event for bracket association."""
    event_repo = EventRepository(async_session)
    event_create = EventCreate(
        server_id=server_id,
        name="Bracket Test Event",
        match_type=EventMatchType.SINGLE,
        use_application=True,
        is_public=True,
        team_size=5,
        team_formation=TeamFormation.BALANCE,
        allow_multiple_drafts=False
    )
    return await event_repo.create(event_create)


@pytest.fixture
def bracket_repo(async_session):
    """Fixture providing BracketRepository instance."""
    return BracketRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    """Fixture providing EventRepository instance."""
    return EventRepository(async_session)


class TestBracketRepository:
    """Test suite for BracketRepository operations."""

    async def test_create_bracket(self, bracket_repo, event_dto):
        """
        Test: Creating a bracket successfully.
        When: BracketCreate DTO is passed with valid event_id.
        Then: Bracket is created and returned with correct attributes.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )

        # Act
        created_bracket = await bracket_repo.create(bracket_create)

        # Assert
        assert created_bracket.id is not None
        assert created_bracket.event_id == event_dto.id
        assert isinstance(created_bracket, Bracket)

    async def test_create_bracket_foreign_key_violation(self, bracket_repo):
        """
        Test: Creating bracket with non-existent event_id raises exception.
        When: BracketCreate uses random UUID for event_id.
        Then: IntegrityForeignException is raised on flush.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=uuid4()  # Non-existent event
        )

        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await bracket_repo.create(bracket_create)

    async def test_get_bracket_by_id(self, bracket_repo, event_dto):
        """
        Test: Retrieving bracket by ID.
        When: Valid bracket ID is passed.
        Then: Bracket is returned with matching attributes.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)

        # Act
        retrieved = await bracket_repo.get(created.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id

    async def test_get_non_existent_bracket_returns_none(self, bracket_repo):
        """
        Test: Retrieving non-existent bracket returns None.
        When: Random UUID is passed as bracket_id.
        Then: None is returned instead of raising exception.
        """
        # Act
        result = await bracket_repo.get(uuid4())

        # Assert
        assert result is None

    async def test_get_bracket_with_event_relation(self, bracket_repo, event_dto):
        """
        Test: Loading bracket with related stages.
        When: load_stages=True flag is passed.
        Then: Bracket is returned with stages relationship populated.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)

        # Act
        retrieved = await bracket_repo.get(created.id, load_stages=True)

        # Assert
        assert retrieved is not None
        assert hasattr(retrieved, 'stages')

    async def test_get_bracket_with_stages_relation(self, bracket_repo, event_dto):
        """
        Test: Loading bracket with related stages.
        When: load_stages=True flag is passed.
        Then: Bracket is returned with stages relationship populated.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)

        # Act
        retrieved = await bracket_repo.get(created.id, load_stages=True)

        # Assert
        assert retrieved is not None
        assert hasattr(retrieved, 'stages')

    async def test_list_by_event(self, bracket_repo, event_dto):
        """
        Test: Listing all brackets for a specific event.
        When: Multiple brackets are created for the same event.
        Then: list_by_event returns all of them.
        """
        # Arrange
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))

        # Act
        brackets = await bracket_repo.list_by_event(event_dto.id)

        # Assert
        assert len(brackets) == 3
        assert all(bracket.event_id == event_dto.id for bracket in brackets)

    async def test_list_by_event_with_pagination(self, bracket_repo, event_dto):
        """
        Test: Listing brackets with pagination.
        When: Multiple brackets exist and offset/limit are specified.
        Then: Returned list respects pagination boundaries.
        """
        # Arrange
        for i in range(5):
            await bracket_repo.create(
                BracketCreate(event_id=event_dto.id)
            )

        # Act
        page_1 = await bracket_repo.list_by_event(event_dto.id, offset=0, limit=2)
        page_2 = await bracket_repo.list_by_event(event_dto.id, offset=2, limit=2)
        page_3 = await bracket_repo.list_by_event(event_dto.id, offset=4, limit=2)

        # Assert
        assert len(page_1) == 2
        assert len(page_2) == 2
        assert len(page_3) == 1

    async def test_list_by_event_empty_when_no_brackets(self, bracket_repo, event_dto):
        """
        Test: Listing brackets for event with no brackets returns empty list.
        When: list_by_event is called for an event with zero brackets.
        Then: Empty list is returned.
        """
        # Act
        brackets = await bracket_repo.list_by_event(event_dto.id)

        # Assert
        assert len(brackets) == 0

    async def test_list_by_non_existent_event_returns_empty(self, bracket_repo):
        """
        Test: Listing brackets for non-existent event returns empty list.
        When: list_by_event is called with a random UUID.
        Then: Empty list is returned (no exception).
        """
        # Act
        brackets = await bracket_repo.list_by_event(uuid4())

        # Assert
        assert len(brackets) == 0

    async def test_delete_bracket(self, bracket_repo, event_dto):
        """
        Test: Deleting a bracket.
        When: delete is called with valid bracket_id.
        Then: Bracket is removed and subsequent get returns None.
        """
        # Arrange
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)

        # Act
        delete_result = await bracket_repo.delete(created.id)

        # Assert
        assert delete_result is True
        retrieved_after_delete = await bracket_repo.get(created.id)
        assert retrieved_after_delete is None

    async def test_delete_non_existent_bracket_returns_false(self, bracket_repo):
        """
        Test: Deleting non-existent bracket returns False.
        When: delete is called with random UUID.
        Then: False is returned (no exception).
        """
        # Act
        result = await bracket_repo.delete(uuid4())

        # Assert
        assert result is False

    async def test_list_brackets_different_events_isolated(self, bracket_repo, event_repo, server_id):
        """
        Test: Brackets from different events are isolated.
        When: Multiple events have brackets.
        Then: list_by_event returns only brackets for that specific event.
        """
        # Arrange
        event1 = await event_repo.create(
            EventCreate(server_id=server_id, name="Event 1", match_type=EventMatchType.SINGLE, use_application=True,
                        is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        event2 = await event_repo.create(
            EventCreate(server_id=server_id, name="Event 2", match_type=EventMatchType.SINGLE, use_application=True,
                        is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))

        await bracket_repo.create(BracketCreate(event_id=event1.id))
        await bracket_repo.create(BracketCreate(event_id=event2.id))

        # Act
        event1_brackets = await bracket_repo.list_by_event(event1.id)
        event2_brackets = await bracket_repo.list_by_event(event2.id)

        # Assert
        assert len(event1_brackets) == 1
        assert len(event2_brackets) == 1
        assert event1_brackets[0].event_id == event1.id
        assert event2_brackets[0].event_id == event2.id
