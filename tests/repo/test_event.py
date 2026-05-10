import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus, EventUpdate, TeamFormation
from src.infra.postgre.repo.event import EventRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
def repo(async_session: AsyncSession) -> EventRepository:
    return EventRepository(async_session)


class TestEventRepository:
    async def test_create_and_get_event(self, repo: EventRepository):
        server_id = uuid.uuid4()
        event = await repo.create(
            EventCreate(
                name="Alpha Event",
                match_type=EventMatchType.TOURNAMENT,
                use_application=False,
                is_public=False,
                team_size=2,
                team_formation=TeamFormation.MANUAL,
                allow_multiple_drafts=True,
                server_id=server_id,
            )
        )

        fetched = await repo.get(event.id)

        assert event.id is not None
        assert event.name == "Alpha Event"
        assert event.match_type == EventMatchType.TOURNAMENT
        assert event.status == EventStatus.CREATED
        assert fetched is not None
        assert fetched.id == event.id
        assert fetched.server_id == server_id

    async def test_get_non_existent_returns_none(self, repo: EventRepository):
        assert await repo.get(uuid.uuid4()) is None

    async def test_get_with_relations_on_empty_relationships(self, repo: EventRepository):
        event = await repo.create(
            EventCreate(
                name="Rel Event",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=uuid.uuid4(),
            )
        )

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

    async def test_update_event(self, repo: EventRepository):
        event = await repo.create(
            EventCreate(
                name="Old Name",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=uuid.uuid4(),
            )
        )

        updated = await repo.update(event.id, EventUpdate(name="New Name", team_size=3))
        fetched = await repo.get(event.id)

        assert updated.name == "New Name"
        assert updated.team_size == 3
        assert updated.match_type == EventMatchType.SINGLE
        assert fetched is not None
        assert fetched.name == "New Name"

    async def test_update_missing_event_raises_not_found(self, repo: EventRepository):
        with pytest.raises(NotFoundException):
            await repo.update(uuid.uuid4(), EventUpdate(name="Nope"))

    async def test_transition_status(self, repo: EventRepository):
        event = await repo.create(
            EventCreate(
                name="Transition",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=uuid.uuid4(),
            )
        )

        transitioned = await repo.transition_status(event.id, EventStatus.REGISTRATION)
        assert transitioned.status == EventStatus.REGISTRATION

        same_status = await repo.transition_status(event.id, EventStatus.REGISTRATION)
        assert same_status.status == EventStatus.REGISTRATION

    async def test_transition_status_invalid_raises_conflict(self, repo: EventRepository):
        event = await repo.create(
            EventCreate(
                name="Invalid Transition",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=uuid.uuid4(),
            )
        )

        with pytest.raises(ConflictException):
            await repo.transition_status(event.id, EventStatus.IN_PROGRESS)

    async def test_transition_status_missing_event_raises_not_found(self, repo: EventRepository):
        with pytest.raises(NotFoundException):
            await repo.transition_status(uuid.uuid4(), EventStatus.REGISTRATION)

    async def test_list_public_and_by_server(self, repo: EventRepository):
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()

        public_s1 = await repo.create(
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
        private_s1 = await repo.create(
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
        public_s2 = await repo.create(
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

        public_events = await repo.list_public(0, 10)
        server_1_events = await repo.list_by_server(s1, 0, 10)
        server_1_public = await repo.list_public_by_server(s1, 0, 10)

        assert {e.id for e in public_events} == {public_s1.id, public_s2.id}
        assert {e.id for e in server_1_events} == {public_s1.id, private_s1.id}
        assert {e.id for e in server_1_public} == {public_s1.id}

    async def test_delete_event(self, repo: EventRepository):
        event = await repo.create(
            EventCreate(
                name="Del Event",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
                server_id=uuid.uuid4(),
            )
        )

        assert await repo.delete(event.id) is True
        assert await repo.delete(uuid.uuid4()) is False
        assert await repo.get(event.id) is None
