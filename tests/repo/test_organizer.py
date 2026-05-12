import uuid

import pytest

from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.core.models.organizer import OrganizerCreate
from src.infra.postgre.exceptions import IntegrityForeignException

pytestmark = pytest.mark.asyncio


class TestOrganizerRepository:
    async def test_create_organizer(self, organizer_repo, event_dto):
        created = await organizer_repo.create(
            OrganizerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )

        assert created.id is not None
        assert created.event_id == event_dto.id

    async def test_create_organizer_foreign_key_violation(self, organizer_repo):
        with pytest.raises(IntegrityForeignException):
            await organizer_repo.create(
                OrganizerCreate(event_id=uuid.uuid4(), member_id=uuid.uuid4())
            )

    async def test_get_organizer_by_id(self, organizer_repo, event_dto):
        created = await organizer_repo.create(
            OrganizerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )
        retrieved = await organizer_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id

    async def test_get_non_existent_organizer_returns_none(self, organizer_repo):
        assert await organizer_repo.get(uuid.uuid4()) is None

    async def test_get_organizer_with_event_relation(self, organizer_repo, event_dto):
        created = await organizer_repo.create(
            OrganizerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )
        retrieved = await organizer_repo.get(created.id, load_event=True)

        assert retrieved is not None
        assert retrieved.event is not None
        assert retrieved.event.id == event_dto.id
        assert retrieved.event.name == event_dto.name

    async def test_list_by_event(self, organizer_repo, event_dto):
        for _ in range(3):
            await organizer_repo.create(OrganizerCreate(event_id=event_dto.id, member_id=uuid.uuid4()))

        organizers = await organizer_repo.list_by_event(event_dto.id)

        assert len(organizers) == 3
        assert all(org.event_id == event_dto.id for org in organizers)

    async def test_list_by_event_empty_when_no_organizers(self, organizer_repo, event_dto):
        assert await organizer_repo.list_by_event(event_dto.id) == []

    async def test_list_by_non_existent_event_returns_empty(self, organizer_repo):
        assert await organizer_repo.list_by_event(uuid.uuid4()) == []

    async def test_delete_organizer(self, organizer_repo, event_dto):
        created = await organizer_repo.create(
            OrganizerCreate(event_id=event_dto.id, member_id=uuid.uuid4())
        )

        assert await organizer_repo.delete(created.id) is True
        assert await organizer_repo.get(created.id) is None

    async def test_delete_non_existent_organizer_returns_false(self, organizer_repo):
        assert await organizer_repo.delete(uuid.uuid4()) is False

    async def test_list_multiple_events_organizers_isolated(self, organizer_repo, event_repo, server_id):
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
            )
        )

        await organizer_repo.create(OrganizerCreate(event_id=event1.id, member_id=uuid.uuid4()))
        await organizer_repo.create(OrganizerCreate(event_id=event2.id, member_id=uuid.uuid4()))

        event1_orgs = await organizer_repo.list_by_event(event1.id)
        event2_orgs = await organizer_repo.list_by_event(event2.id)

        assert len(event1_orgs) == 1
        assert len(event2_orgs) == 1
        assert event1_orgs[0].event_id == event1.id
        assert event2_orgs[0].event_id == event2.id

