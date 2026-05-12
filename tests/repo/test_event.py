import uuid

import pytest

from src.core.exceptions import ConflictException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus, EventUpdate, TeamFormation
from src.infra.postgre.repo.event import EventRepository

pytestmark = pytest.mark.asyncio


class TestEventRepository:
    async def test_create_and_get_event(self, event_repo: EventRepository, server_id: uuid.UUID):
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

        event = await event_repo.create(event_create)
        fetched = await event_repo.get(event.id)

        assert event.id is not None
        assert event.name == "Alpha Event"
        assert event.match_type == EventMatchType.TOURNAMENT
        assert event.status == EventStatus.CREATED
        assert fetched is not None
        assert fetched.id == event.id
        assert fetched.server_id == server_id

    async def test_get_non_existent_returns_none(self, event_repo: EventRepository):
        result = await event_repo.get(uuid.uuid4())

        assert result is None

    async def test_get_with_relations_on_empty_relationships(self, event_repo: EventRepository, server_id: uuid.UUID):
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
        event = await event_repo.create(event_create)

        fetched = await event_repo.get(
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

    async def test_update_event(self, event_repo: EventRepository, event_dto):
        event_update = EventUpdate(name="New Name", team_size=3)

        updated = await event_repo.update(event_dto.id, event_update)
        fetched = await event_repo.get(event_dto.id)

        assert updated.name == "New Name"
        assert updated.team_size == 3
        assert updated.match_type == EventMatchType.SINGLE
        assert fetched is not None
        assert fetched.name == "New Name"

    async def test_update_missing_event_raises_not_found(self, event_repo: EventRepository):
        event_update = EventUpdate(name="Nope")

        with pytest.raises(NotFoundException):
            await event_repo.update(uuid.uuid4(), event_update)

    async def test_update_preserves_other_fields(self, event_repo: EventRepository, event_dto):
        original_match_type = event_dto.match_type
        event_update = EventUpdate(name="Updated Name")

        updated = await event_repo.update(event_dto.id, event_update)

        assert updated.name == "Updated Name"
        assert updated.match_type == original_match_type
        assert updated.team_size == event_dto.team_size

    async def test_transition_status(self, event_repo: EventRepository, event_dto):
        transitioned = await event_repo.transition_status(event_dto.id, EventStatus.REGISTRATION)
        same_status = await event_repo.transition_status(event_dto.id, EventStatus.REGISTRATION)

        assert transitioned.status == EventStatus.REGISTRATION
        assert same_status.status == EventStatus.REGISTRATION

    async def test_transition_status_invalid_raises_conflict(self, event_repo: EventRepository, event_dto):
        with pytest.raises(ConflictException):
            await event_repo.transition_status(event_dto.id, EventStatus.IN_PROGRESS)

    async def test_transition_status_missing_event_raises_not_found(self, event_repo: EventRepository):
        with pytest.raises(NotFoundException):
            await event_repo.transition_status(uuid.uuid4(),  EventStatus.REGISTRATION)

    async def test_transition_status_sequence(self, event_repo: EventRepository, event_dto):
        statuses = [EventStatus.REGISTRATION, EventStatus.FORMATION, EventStatus.IN_PROGRESS, EventStatus.COMPLETED]

        current_event = event_dto
        for status in statuses:
            current_event = await event_repo.transition_status(current_event.id, status)
            assert current_event.status == status

    async def test_list_public_and_by_server(self, event_repo: EventRepository):
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()

        public_s1 = await event_repo.create(
            EventCreate(
                name="Public 1",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=s1,
            )
        )
        private_s1 = await event_repo.create(
            EventCreate(
                name="Private 1",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=False,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=s1,
            )
        )
        public_s2 = await event_repo.create(
            EventCreate(
                name="Public 2",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=s2,
            )
        )

        public_events = await event_repo.list_public(0, 10)
        server_1_events = await event_repo.list_by_server(s1, 0, 10)
        server_1_public = await event_repo.list_public_by_server(s1, 0, 10)

        assert {e.id for e in public_events} == {public_s1.id, public_s2.id}
        assert {e.id for e in server_1_events} == {public_s1.id, private_s1.id}
        assert {e.id for e in server_1_public} == {public_s1.id}

    async def test_list_pagination(self, event_repo: EventRepository):
        server_id = uuid.uuid4()

        for i in range(5):
            await event_repo.create(
                EventCreate(
                    name=f"Event {i}",
                    match_type=EventMatchType.SINGLE,
                    use_application=True,
                    is_public=True,
                    team_size=5,
                    team_formation=TeamFormation.BALANCE,
                    allow_multiple_drafts=False,
                    server_id=server_id,
                )
            )

        page1 = await event_repo.list_by_server(server_id, offset=0, limit=2)
        page2 = await event_repo.list_by_server(server_id, offset=2, limit=2)
        page3 = await event_repo.list_by_server(server_id, offset=4, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_list_empty_results(self, event_repo: EventRepository):
        non_existent_server_id = uuid.uuid4()

        result = await event_repo.list_by_server(non_existent_server_id, 0, 10)

        assert result == []
        assert len(result) == 0

    async def test_delete_event(self, event_repo: EventRepository, event_dto):
        delete_success = await event_repo.delete(event_dto.id)
        delete_fail = await event_repo.delete(uuid.uuid4())
        fetched_after_delete = await event_repo.get(event_dto.id)

        assert delete_success is True
        assert delete_fail is False
        assert fetched_after_delete is None

    async def test_delete_non_existent_returns_false(self, event_repo: EventRepository):
        result = await event_repo.delete(uuid.uuid4())
        assert result is False
