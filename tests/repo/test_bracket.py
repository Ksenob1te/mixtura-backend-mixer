from uuid import UUID, uuid4

import pytest

from src.core.models.bracket import Bracket, BracketCreate
from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.infra.postgre.repo.bracket import BracketRepository
from src.infra.postgre.repo.event import EventRepository
from src.infra.postgre.exceptions import IntegrityForeignException


@pytest.fixture
def server_id() -> UUID:
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
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
    return BracketRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    return EventRepository(async_session)


class TestBracketRepository:

    async def test_create_bracket(self, bracket_repo, event_dto):
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created_bracket = await bracket_repo.create(bracket_create)

        assert created_bracket.id is not None
        assert created_bracket.event_id == event_dto.id
        assert isinstance(created_bracket, Bracket)

    async def test_create_bracket_foreign_key_violation(self, bracket_repo):
        bracket_create = BracketCreate(
            event_id=uuid4()
        )

        with pytest.raises(IntegrityForeignException):
            await bracket_repo.create(bracket_create)

    async def test_get_bracket_by_id(self, bracket_repo, event_dto):
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)

        retrieved = await bracket_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id

    async def test_get_non_existent_bracket_returns_none(self, bracket_repo):
        result = await bracket_repo.get(uuid4())
        assert result is None

    async def test_get_bracket_with_event_relation(self, bracket_repo, event_dto):
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)
        retrieved = await bracket_repo.get(created.id, load_stages=True)

        assert retrieved is not None
        assert hasattr(retrieved, 'stages')

    async def test_get_bracket_with_stages_relation(self, bracket_repo, event_dto):
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)
        retrieved = await bracket_repo.get(created.id, load_stages=True)

        assert retrieved is not None
        assert hasattr(retrieved, 'stages')

    async def test_list_by_event(self, bracket_repo, event_dto):
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        await bracket_repo.create(BracketCreate(event_id=event_dto.id))

        brackets = await bracket_repo.list_by_event(event_dto.id)

        assert len(brackets) == 3
        assert all(bracket.event_id == event_dto.id for bracket in brackets)

    async def test_list_by_event_with_pagination(self, bracket_repo, event_dto):
        for i in range(5):
            await bracket_repo.create(
                BracketCreate(event_id=event_dto.id)
            )

        page_1 = await bracket_repo.list_by_event(event_dto.id, offset=0, limit=2)
        page_2 = await bracket_repo.list_by_event(event_dto.id, offset=2, limit=2)
        page_3 = await bracket_repo.list_by_event(event_dto.id, offset=4, limit=2)

        assert len(page_1) == 2
        assert len(page_2) == 2
        assert len(page_3) == 1

    async def test_list_by_event_empty_when_no_brackets(self, bracket_repo, event_dto):
        brackets = await bracket_repo.list_by_event(event_dto.id)
        assert len(brackets) == 0

    async def test_list_by_non_existent_event_returns_empty(self, bracket_repo):
        brackets = await bracket_repo.list_by_event(uuid4())

        assert len(brackets) == 0

    async def test_delete_bracket(self, bracket_repo, event_dto):
        bracket_create = BracketCreate(
            event_id=event_dto.id
        )
        created = await bracket_repo.create(bracket_create)
        delete_result = await bracket_repo.delete(created.id)

        assert delete_result is True
        retrieved_after_delete = await bracket_repo.get(created.id)
        assert retrieved_after_delete is None

    async def test_delete_non_existent_bracket_returns_false(self, bracket_repo):
        result = await bracket_repo.delete(uuid4())
        assert result is False

    async def test_list_brackets_different_events_isolated(self, bracket_repo, event_repo, server_id):
        event1 = await event_repo.create(
            EventCreate(server_id=server_id, name="Event 1", match_type=EventMatchType.SINGLE, use_application=True,
                        is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        event2 = await event_repo.create(
            EventCreate(server_id=server_id, name="Event 2", match_type=EventMatchType.SINGLE, use_application=True,
                        is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))

        await bracket_repo.create(BracketCreate(event_id=event1.id))
        await bracket_repo.create(BracketCreate(event_id=event2.id))

        event1_brackets = await bracket_repo.list_by_event(event1.id)
        event2_brackets = await bracket_repo.list_by_event(event2.id)

        assert len(event1_brackets) == 1
        assert len(event2_brackets) == 1
        assert event1_brackets[0].event_id == event1.id
        assert event2_brackets[0].event_id == event2.id
