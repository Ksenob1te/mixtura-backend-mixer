import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus, EventUpdate, TeamFormation, Event
from src.infra.postgre.repo.event import EventRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
def repo(async_session: AsyncSession) -> EventRepository:
    return EventRepository(async_session)


@pytest.fixture
def server_id() -> uuid.UUID:
    """Fixture providing a unique server ID for tests."""
    return uuid.uuid4()


@pytest.fixture
async def base_event(repo: EventRepository, server_id: uuid.UUID) -> Event:
    """Fixture providing a base event for tests."""
    return await repo.create(EventCreate(
        name="Base Test Event",
        match_type=EventMatchType.SINGLE,
        use_application=True,
        is_public=True,
        team_size=5,
        team_formation=TeamFormation.BALANCE,
        allow_multiple_drafts=False,
        server_id=server_id
    ))


class TestEventRepository:
    async def test_create_and_get_event(self, repo: EventRepository, server_id: uuid.UUID):
        """Test basic event creation and retrieval."""
        event_create = EventCreate(
            name="Alpha Event",
            match_type=EventMatchType.TOURNAMENT,
            use_application=False,
            is_public=False,
            team_size=2,
            team_formation=TeamFormation.MANUAL,
            allow_multiple_drafts=True,
            server_id=server_id,
        )

        # Act
        event = await repo.create(event_create)
        fetched = await repo.get(event.id)

        # Assert
        assert event.id is not None
        assert event.name == "Alpha Event"
        assert event.match_type == EventMatchType.TOURNAMENT
        assert event.status == EventStatus.CREATED
        assert fetched is not None
        assert fetched.id == event.id
        assert fetched.server_id == server_id

    async def test_get_non_existent_returns_none(self, repo: EventRepository):
        """Test that getting non-existent event returns None."""
        # Act
        result = await repo.get(uuid.uuid4())

        # Assert
        assert result is None

    async def test_get_with_relations_on_empty_relationships(self, repo: EventRepository, server_id: uuid.UUID):
        """Test loading all relations when event has no nested data."""
        event_create = EventCreate(
            name="Rel Event",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
            server_id=server_id,
        )
        event = await repo.create(event_create)

        # Act
        fetched = await repo.get(
            event.id,
            load_time_settings=True,
            load_custom_fields=True,
            load_game_roles=True,
            load_integrations=True,
            load_organizers=True,
            load_applications=True,
            load_teams=True,
            load_drafts=True,
            load_players=True,
            load_brackets=True,
        )

        # Assert
        assert fetched is not None
        assert fetched.applications == []
        assert fetched.teams == []
        assert fetched.drafts == []
        assert fetched.organizers == []
        assert fetched.event_players == []
        assert fetched.brackets == []
        assert fetched.required_integrations == []
        assert fetched.selected_game_roles == []
        assert fetched.custom_fields == []
        assert fetched.time_settings is None

    async def test_update_event(self, repo: EventRepository, base_event: Event):
        """Test event update with partial fields."""
        event_update = EventUpdate(name="New Name", team_size=3)

        # Act
        updated = await repo.update(base_event.id, event_update)
        fetched = await repo.get(base_event.id)

        # Assert
        assert updated.name == "New Name"
        assert updated.team_size == 3
        assert updated.match_type == EventMatchType.SINGLE
        assert fetched is not None
        assert fetched.name == "New Name"

    async def test_update_missing_event_raises_not_found(self, repo: EventRepository):
        """Test that updating non-existent event raises NotFoundException."""
        event_update = EventUpdate(name="Nope")

        # Act & Assert
        with pytest.raises(NotFoundException):
            await repo.update(uuid.uuid4(), event_update)

    async def test_update_preserves_other_fields(self, repo: EventRepository, base_event: Event):
        """Test that updating one field preserves others."""
        original_match_type = base_event.match_type
        event_update = EventUpdate(name="Updated Name")

        # Act
        updated = await repo.update(base_event.id, event_update)

        # Assert
        assert updated.name == "Updated Name"
        assert updated.match_type == original_match_type
        assert updated.team_size == base_event.team_size

    async def test_transition_status(self, repo: EventRepository, base_event: Event):
        """Test valid status transitions."""
        # Act
        transitioned = await repo.transition_status(base_event.id, EventStatus.REGISTRATION)
        same_status = await repo.transition_status(base_event.id, EventStatus.REGISTRATION)

        # Assert
        assert transitioned.status == EventStatus.REGISTRATION
        assert same_status.status == EventStatus.REGISTRATION

    async def test_transition_status_invalid_raises_conflict(self, repo: EventRepository, base_event: Event):
        """Test that invalid status transition raises ConflictException."""
        # Act & Assert - IN_PROGRESS is not reachable from CREATED directly
        with pytest.raises(ConflictException):
            await repo.transition_status(base_event.id, EventStatus.IN_PROGRESS)

    async def test_transition_status_missing_event_raises_not_found(self, repo: EventRepository):
        """Test that transitioning non-existent event raises NotFoundException."""
        # Act & Assert
        with pytest.raises(NotFoundException):
            await repo.transition_status(uuid.uuid4(), EventStatus.REGISTRATION)

    async def test_transition_status_sequence(self, repo: EventRepository, base_event: Event):
        """Test a valid sequence of status transitions."""
        statuses = [
            EventStatus.REGISTRATION,
            EventStatus.FORMATION,
            EventStatus.IN_PROGRESS,
            EventStatus.COMPLETED
        ]

        # Act & Assert
        current_event = base_event
        for status in statuses:
            current_event = await repo.transition_status(current_event.id, status)
            assert current_event.status == status

    async def test_list_public_and_by_server(self, repo: EventRepository):
        """Test filtering events by public flag and server."""
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()

        # Act - Create test events
        public_s1 = await repo.create(EventCreate(
            name="Public 1", match_type=EventMatchType.SINGLE, use_application=True,
            is_public=True, team_size=5, team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False, server_id=s1,
        ))
        private_s1 = await repo.create(EventCreate(
            name="Private 1", match_type=EventMatchType.SINGLE, use_application=True,
            is_public=False, team_size=5, team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False, server_id=s1,
        ))
        public_s2 = await repo.create(EventCreate(
            name="Public 2", match_type=EventMatchType.SINGLE, use_application=True,
            is_public=True, team_size=5, team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False, server_id=s2,
        ))

        # Query
        public_events = await repo.list_public(0, 10)
        server_1_events = await repo.list_by_server(s1, 0, 10)
        server_1_public = await repo.list_public_by_server(s1, 0, 10)

        # Assert
        assert {e.id for e in public_events} == {public_s1.id, public_s2.id}
        assert {e.id for e in server_1_events} == {public_s1.id, private_s1.id}
        assert {e.id for e in server_1_public} == {public_s1.id}

    async def test_list_pagination(self, repo: EventRepository):
        """Test pagination on list queries."""
        server_id = uuid.uuid4()

        # Act - Create multiple events
        for i in range(5):
            await repo.create(EventCreate(
                name=f"Event {i}", match_type=EventMatchType.SINGLE, use_application=True,
                is_public=True, team_size=5, team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False, server_id=server_id,
            ))

        # Query with pagination
        page1 = await repo.list_by_server(server_id, offset=0, limit=2)
        page2 = await repo.list_by_server(server_id, offset=2, limit=2)
        page3 = await repo.list_by_server(server_id, offset=4, limit=2)

        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_list_empty_results(self, repo: EventRepository):
        """Test list methods return empty when no matches."""
        non_existent_server_id = uuid.uuid4()

        # Act
        result = await repo.list_by_server(non_existent_server_id, 0, 10)

        # Assert
        assert result == []
        assert len(result) == 0

    async def test_delete_event(self, repo: EventRepository, base_event: Event):
        """Test event deletion."""
        # Act
        delete_success = await repo.delete(base_event.id)
        delete_fail = await repo.delete(uuid.uuid4())
        fetched_after_delete = await repo.get(base_event.id)

        # Assert
        assert delete_success is True
        assert delete_fail is False
        assert fetched_after_delete is None

    async def test_delete_non_existent_returns_false(self, repo: EventRepository):
        """Test that deleting non-existent event returns False."""
        # Act
        result = await repo.delete(uuid.uuid4())

        # Assert
        assert result is False
