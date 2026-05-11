"""
Test suite for MatchRepository using testcontainers + pytest.
Covers CRUD operations, relationship loading, filtering, and edge cases.
"""
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import NotFoundException
from src.core.models.bracket import BracketCreate
from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.core.models.match import Match, MatchCreate, MatchUpdate
from src.core.models.stage import StageCreate, StageFormat
from src.core.models.stage_group import StageGroupCreate
from src.infra.postgre.repo.bracket import BracketRepository
from src.infra.postgre.repo.event import EventRepository
from src.infra.postgre.repo.match import MatchRepository
from src.infra.postgre.repo.stage import StageRepository
from src.infra.postgre.repo.stage_group import StageGroupRepository


@pytest.fixture
def server_id() -> UUID:
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    event_repo = EventRepository(async_session)
    return await event_repo.create(
        EventCreate(
            server_id=server_id,
            name="Match Test Event",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
        )
    )


@pytest.fixture
async def bracket_dto(async_session, event_dto):
    bracket_repo = BracketRepository(async_session)
    return await bracket_repo.create(BracketCreate(event_id=event_dto.id))


@pytest.fixture
async def stage_dto(async_session, bracket_dto):
    stage_repo = StageRepository(async_session)
    return await stage_repo.create(
        StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="Group Stage")
    )


@pytest.fixture
async def stage_group_dto(async_session, stage_dto):
    group_repo = StageGroupRepository(async_session)
    return await group_repo.create(StageGroupCreate(stage_id=stage_dto.id, name="Group A"))


@pytest.fixture
def match_repo(async_session):
    return MatchRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    return EventRepository(async_session)


@pytest.fixture
def bracket_repo(async_session):
    return BracketRepository(async_session)


@pytest.fixture
def stage_repo(async_session):
    return StageRepository(async_session)


@pytest.fixture
def stage_group_repo(async_session):
    return StageGroupRepository(async_session)


class TestMatchRepository:
    async def test_create_match(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        assert isinstance(created, Match)
        assert created.group_id == stage_group_dto.id
        assert created.match_index == 1

    async def test_create_match_foreign_key_violation(self, match_repo):
        with pytest.raises(Exception):
            await match_repo.create(MatchCreate(group_id=uuid4(), match_index=1))

    async def test_get_match_by_id(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=2))
        retrieved = await match_repo.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.match_index == 2

    async def test_get_non_existent_match_returns_none(self, match_repo):
        assert await match_repo.get(uuid4()) is None

    async def test_get_match_with_slots_relation(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        retrieved = await match_repo.get(created.id, load_slots=True)
        assert retrieved is not None
        assert retrieved.slots == []

    async def test_get_match_with_group_relation(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        retrieved = await match_repo.get(created.id, load_group=True)
        assert retrieved is not None
        assert retrieved.group is not None
        assert retrieved.group.id == stage_group_dto.id

    async def test_list_by_stage_group(self, match_repo, stage_group_dto):
        for i in range(3):
            await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=i + 1))

        matches = await match_repo.list_by_stage_group(stage_group_dto.id)
        assert len(matches) == 3
        assert all(match.group_id == stage_group_dto.id for match in matches)

    async def test_list_by_stage_group_with_pagination(self, match_repo, stage_group_dto):
        for i in range(5):
            await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=i + 1))

        assert len(await match_repo.list_by_stage_group(stage_group_dto.id, offset=0, limit=2)) == 2
        assert len(await match_repo.list_by_stage_group(stage_group_dto.id, offset=2, limit=2)) == 2
        assert len(await match_repo.list_by_stage_group(stage_group_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_stage_group_empty_when_no_matches(self, match_repo, stage_group_dto):
        assert await match_repo.list_by_stage_group(stage_group_dto.id) == []

    async def test_next_match_index(self, match_repo, stage_group_dto):
        assert await match_repo.next_match_index(stage_group_dto.id) == 1
        await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=2))
        assert await match_repo.next_match_index(stage_group_dto.id) == 3

    async def test_update_match(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        now = datetime.utcnow()
        updated = await match_repo.update(created.id, MatchUpdate(time_start=now, time_end=now + timedelta(hours=1)))
        assert updated.id == created.id
        assert updated.time_start == now
        assert updated.time_end == now + timedelta(hours=1)

    async def test_update_match_not_found(self, match_repo):
        with pytest.raises(NotFoundException):
            await match_repo.update(uuid4(), MatchUpdate(time_end=datetime.utcnow()))

    async def test_delete_match(self, match_repo, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        assert await match_repo.delete(created.id) is True
        assert await match_repo.get(created.id) is None

    async def test_delete_non_existent_match_returns_false(self, match_repo):
        assert await match_repo.delete(uuid4()) is False

    async def test_list_by_event(self, match_repo, event_dto, stage_group_dto):
        await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=2))
        matches = await match_repo.list_by_event(event_dto.id)
        assert len(matches) == 2

    async def test_list_by_event_with_pagination(self, match_repo, event_dto, stage_group_dto):
        for i in range(5):
            await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=i + 1))
        assert len(await match_repo.list_by_event(event_dto.id, offset=0, limit=2)) == 2
        assert len(await match_repo.list_by_event(event_dto.id, offset=2, limit=2)) == 2

    async def test_list_by_event_filter_active_only(self, match_repo, event_dto, stage_group_dto):
        active = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        completed = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=2))
        now = datetime.utcnow()
        await match_repo.update(active.id, MatchUpdate(time_end=None))
        await match_repo.update(completed.id, MatchUpdate(time_end=now))

        assert len(await match_repo.list_by_event(event_dto.id, active=True)) >= 1
        assert len(await match_repo.list_by_event(event_dto.id, active=False)) >= 1

    async def test_count_incomplete_matches_by_event(self, match_repo, event_dto, stage_group_dto):
        match1 = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        match2 = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=2))
        assert await match_repo.count_incomplete_matches_by_event(event_dto.id) == 2
        await match_repo.update(match1.id, MatchUpdate(time_end=datetime.utcnow()))
        assert await match_repo.count_incomplete_matches_by_event(event_dto.id) == 1
        await match_repo.update(match2.id, MatchUpdate(time_end=datetime.utcnow()))
        assert await match_repo.count_incomplete_matches_by_event(event_dto.id) == 0

    async def test_get_event_context(self, match_repo, event_dto, stage_group_dto):
        created = await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))
        context = await match_repo.get_event_context(created.id)
        assert context is not None
        assert context[0] == event_dto.id
        assert context[1] == event_dto.server_id

    async def test_list_by_event_empty_when_no_matches(self, match_repo, event_dto):
        assert await match_repo.list_by_event(event_dto.id) == []

