from uuid import UUID, uuid4
import pytest

from src.core.models.draft import Draft, DraftCreate, DraftStatus, DraftUpdate
from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.infra.postgre.repo.draft import DraftRepository
from src.infra.postgre.repo.event import EventRepository


@pytest.fixture
def server_id() -> UUID:
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    event_repo = EventRepository(async_session)
    return await event_repo.create(
        EventCreate(
            server_id=server_id,
            name="Draft Test Event",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
        )
    )


@pytest.fixture
def draft_repo(async_session):
    return DraftRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    return EventRepository(async_session)


class TestDraftRepository:
    async def test_create_draft(self, draft_repo, event_dto):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        assert isinstance(created, Draft)
        assert created.event_id == event_dto.id
        assert created.status == DraftStatus.OPEN

    async def test_create_draft_foreign_key_violation(self, draft_repo):
        with pytest.raises(Exception):
            await draft_repo.create(DraftCreate(event_id=uuid4()))

    async def test_get_draft_by_id(self, draft_repo, event_dto):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        retrieved = await draft_repo.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id
        assert retrieved.status == DraftStatus.OPEN

    async def test_get_non_existent_draft_returns_none(self, draft_repo):
        assert await draft_repo.get(uuid4()) is None

    async def test_get_draft_with_drafted_players_relation(self, draft_repo, event_dto):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        retrieved = await draft_repo.get(created.id, load_drafted_players=True)
        assert retrieved is not None
        assert retrieved.drafted_players == []

    async def test_list_by_event(self, draft_repo, event_dto):
        for _ in range(3):
            await draft_repo.create(DraftCreate(event_id=event_dto.id))

        drafts = await draft_repo.list_by_event(event_dto.id)
        assert len(drafts) == 3
        assert all(draft.event_id == event_dto.id for draft in drafts)

    async def test_list_by_event_with_pagination(self, draft_repo, event_dto):
        for _ in range(5):
            await draft_repo.create(DraftCreate(event_id=event_dto.id))

        assert len(await draft_repo.list_by_event(event_dto.id, offset=0, limit=2)) == 2
        assert len(await draft_repo.list_by_event(event_dto.id, offset=2, limit=2)) == 2
        assert len(await draft_repo.list_by_event(event_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_event_empty_when_no_drafts(self, draft_repo, event_dto):
        assert await draft_repo.list_by_event(event_dto.id) == []

    async def test_update_draft(self, draft_repo, event_dto):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        updated = await draft_repo.update(DraftUpdate(id=created.id, status=DraftStatus.BALANCE_REQUESTED))
        assert updated.id == created.id
        assert updated.status == DraftStatus.BALANCE_REQUESTED

    async def test_delete_draft(self, draft_repo, event_dto):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        assert await draft_repo.delete(created.id) is True
        assert await draft_repo.get(created.id) is None

    async def test_delete_non_existent_draft_returns_false(self, draft_repo):
        assert await draft_repo.delete(uuid4()) is False

    async def test_list_drafts_different_events_isolated(self, draft_repo, event_repo, server_id):
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

        await draft_repo.create(DraftCreate(event_id=event1.id))
        await draft_repo.create(DraftCreate(event_id=event2.id))

        assert len(await draft_repo.list_by_event(event1.id)) == 1
        assert len(await draft_repo.list_by_event(event2.id)) == 1

