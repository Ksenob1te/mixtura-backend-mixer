"""
Test suite for OrganizerRepository using testcontainers + pytest.
Tests CRUD operations, relationship loading, and edge cases.
"""
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import NotFoundException
from src.core.models.organizer import Organizer, OrganizerCreate
from src.core.models.event import EventCreate, EventStatus, EventMatchType, TeamFormation
from src.infra.postgre.repo.organizer import OrganizerRepository
from src.infra.postgre.repo.event import EventRepository


@pytest.fixture
def server_id() -> UUID:
    """Fixture providing a unique server ID per test."""
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    """Fixture providing a created event for organizer association."""
    event_repo = EventRepository(async_session)
    event_create = EventCreate(
        server_id=server_id,
        name="Organizer Test Event",
        match_type=EventMatchType.SINGLE,
        use_application=True,
        is_public=True,
        team_size=5,
        team_formation=TeamFormation.BALANCE,
        status=EventStatus.CREATED,
        allow_multiple_drafts=False
    )
    return await event_repo.create(event_create)


@pytest.fixture
def organizer_repo(async_session):
    """Fixture providing OrganizerRepository instance."""
    return OrganizerRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    """Fixture providing EventRepository instance."""
    return EventRepository(async_session)


class TestOrganizerRepository:
    """Test suite for OrganizerRepository operations."""

    async def test_create_organizer(self, organizer_repo, event_dto):
        """
        Test: Creating an organizer successfully.
        When: OrganizerCreate DTO is passed with valid event_id and member_id.
        Then: Organizer is created and returned with correct attributes.
        """
        # Arrange
        organizer_create = OrganizerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )

        # Act
        created_organizer = await organizer_repo.create(organizer_create)

        # Assert
        assert created_organizer.id is not None
        assert created_organizer.event_id == event_dto.id
        assert isinstance(created_organizer, Organizer)

    async def test_create_organizer_foreign_key_violation(self, organizer_repo):
        """
        Test: Creating organizer with non-existent event_id raises exception.
        When: OrganizerCreate uses random UUID for event_id.
        Then: IntegrityForeignException is raised on flush.
        """
        # Arrange
        organizer_create = OrganizerCreate(
            event_id=uuid4(),  # Non-existent event
            member_id=uuid4()
        )

        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await organizer_repo.create(organizer_create)

    async def test_get_organizer_by_id(self, organizer_repo, event_dto):
        """
        Test: Retrieving organizer by ID.
        When: Valid organizer ID is passed.
        Then: Organizer is returned with matching attributes.
        """
        # Arrange
        organizer_create = OrganizerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await organizer_repo.create(organizer_create)

        # Act
        retrieved = await organizer_repo.get(created.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id

    async def test_get_non_existent_organizer_returns_none(self, organizer_repo):
        """
        Test: Retrieving non-existent organizer returns None.
        When: Random UUID is passed as organizer_id.
        Then: None is returned instead of raising exception.
        """
        # Act
        result = await organizer_repo.get(uuid4())

        # Assert
        assert result is None

    async def test_get_organizer_with_event_relation(self, organizer_repo, event_dto):
        """
        Test: Loading organizer with related event.
        When: load_event=True flag is passed.
        Then: Organizer is returned with event relationship populated.
        """
        # Arrange
        organizer_create = OrganizerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await organizer_repo.create(organizer_create)

        # Act
        retrieved = await organizer_repo.get(created.id, load_event=True)

        # Assert
        assert retrieved is not None
        assert retrieved.event is not None
        assert retrieved.event.id == event_dto.id
        assert retrieved.event.name == event_dto.name

    async def test_list_by_event(self, organizer_repo, event_dto):
        """
        Test: Listing all organizers for a specific event.
        When: Multiple organizers are created for the same event.
        Then: list_by_event returns all of them.
        """
        # Arrange
        member_id_1 = uuid4()
        member_id_2 = uuid4()
        member_id_3 = uuid4()

        await organizer_repo.create(OrganizerCreate(event_id=event_dto.id, member_id=member_id_1))
        await organizer_repo.create(OrganizerCreate(event_id=event_dto.id, member_id=member_id_2))
        await organizer_repo.create(OrganizerCreate(event_id=event_dto.id, member_id=member_id_3))

        # Act
        organizers = await organizer_repo.list_by_event(event_dto.id)

        # Assert
        assert len(organizers) == 3
        assert all(org.event_id == event_dto.id for org in organizers)

    async def test_list_by_event_empty_when_no_organizers(self, organizer_repo, event_dto):
        """
        Test: Listing organizers for event with no organizers returns empty list.
        When: list_by_event is called for an event with zero organizers.
        Then: Empty list is returned.
        """
        # Act
        organizers = await organizer_repo.list_by_event(event_dto.id)

        # Assert
        assert len(organizers) == 0

    async def test_list_by_non_existent_event_returns_empty(self, organizer_repo):
        """
        Test: Listing organizers for non-existent event returns empty list.
        When: list_by_event is called with a random UUID.
        Then: Empty list is returned (no exception).
        """
        # Act
        organizers = await organizer_repo.list_by_event(uuid4())

        # Assert
        assert len(organizers) == 0

    async def test_delete_organizer(self, organizer_repo, event_dto):
        """
        Test: Deleting an organizer.
        When: delete is called with valid organizer_id.
        Then: Organizer is removed and subsequent get returns None.
        """
        # Arrange
        organizer_create = OrganizerCreate(
            event_id=event_dto.id,
            member_id=uuid4()
        )
        created = await organizer_repo.create(organizer_create)

        # Act
        delete_result = await organizer_repo.delete(created.id)

        # Assert
        assert delete_result is True
        retrieved_after_delete = await organizer_repo.get(created.id)
        assert retrieved_after_delete is None

    async def test_delete_non_existent_organizer_returns_false(self, organizer_repo):
        """
        Test: Deleting non-existent organizer returns False.
        When: delete is called with random UUID.
        Then: False is returned (no exception).
        """
        # Act
        result = await organizer_repo.delete(uuid4())

        # Assert
        assert result is False

    async def test_list_multiple_events_organizers_isolated(self, organizer_repo, event_repo, server_id):
        """
        Test: Organizers from different events are isolated.
        When: Multiple events have organizers.
        Then: list_by_event returns only organizers for that specific event.
        """
        # Arrange
        event1 = await event_repo.create(EventCreate(server_id=server_id, name="Event 1", match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, status=EventStatus.CREATED, allow_multiple_drafts=False))
        event2 = await event_repo.create(EventCreate(server_id=server_id, name="Event 2", match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, status=EventStatus.CREATED, allow_multiple_drafts=False))

        org1_member = uuid4()
        org2_member = uuid4()

        await organizer_repo.create(OrganizerCreate(event_id=event1.id, member_id=org1_member))
        await organizer_repo.create(OrganizerCreate(event_id=event2.id, member_id=org2_member))

        # Act
        event1_orgs = await organizer_repo.list_by_event(event1.id)
        event2_orgs = await organizer_repo.list_by_event(event2.id)

        # Assert
        assert len(event1_orgs) == 1
        assert len(event2_orgs) == 1
        assert event1_orgs[0].event_id == event1.id
        assert event2_orgs[0].event_id == event2.id






