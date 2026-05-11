"""
Test suite for StageRepository using testcontainers + pytest.
Covers CRUD operations, relationship loading, pagination, and edge cases.
"""
from uuid import UUID, uuid4

import pytest

from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.core.models.bracket import BracketCreate
from src.core.models.stage import Stage, StageCreate, StageFormat, StageUpdate
from src.infra.postgre.repo.bracket import BracketRepository
from src.infra.postgre.repo.event import EventRepository
from src.infra.postgre.repo.stage import StageRepository


@pytest.fixture
def server_id() -> UUID:
    return uuid4()


@pytest.fixture
async def event_dto(async_session, server_id):
    event_repo = EventRepository(async_session)
    return await event_repo.create(
        EventCreate(
            server_id=server_id,
            name="Stage Test Event",
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
def stage_repo(async_session):
    return StageRepository(async_session)


@pytest.fixture
def event_repo(async_session):
    return EventRepository(async_session)


@pytest.fixture
def bracket_repo(async_session):
    return BracketRepository(async_session)


class TestStageRepository:
    async def test_create_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="Stage 1")
        )
        assert isinstance(created, Stage)
        assert created.bracket_id == bracket_dto.id
        assert created.stage_index == 1
        assert created.format == StageFormat.ROUND_ROBIN

    async def test_create_stage_foreign_key_violation(self, stage_repo):
        with pytest.raises(Exception):
            await stage_repo.create(
                StageCreate(stage_index=1, bracket_id=uuid4(), format=StageFormat.ROUND_ROBIN, name="Invalid")
            )

    async def test_get_stage_by_id(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.SINGLE_ELIMINATION, name="Lookup")
        )
        retrieved = await stage_repo.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Lookup"

    async def test_get_stage_with_groups_relation(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="Groups")
        )
        retrieved = await stage_repo.get(created.id, load_groups=True)
        assert retrieved is not None
        assert retrieved.groups == []

    async def test_get_stage_with_settings_relation(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.SWISS, name="Settings")
        )
        retrieved = await stage_repo.get(created.id, load_settings=True)
        assert retrieved is not None
        assert retrieved.round_robin_settings is None
        assert retrieved.swiss_settings is None

    async def test_list_by_bracket(self, stage_repo, bracket_dto):
        for i in range(3):
            await stage_repo.create(
                StageCreate(stage_index=i + 1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name=f"Stage {i+1}")
            )

        stages = await stage_repo.list_by_bracket(bracket_dto.id)
        assert len(stages) == 3
        assert all(stage.bracket_id == bracket_dto.id for stage in stages)

    async def test_list_by_bracket_with_pagination(self, stage_repo, bracket_dto):
        for i in range(5):
            await stage_repo.create(
                StageCreate(stage_index=i + 1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name=f"Stage {i+1}")
            )

        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=0, limit=2)) == 2
        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=2, limit=2)) == 2
        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_bracket_empty_when_no_stages(self, stage_repo, bracket_dto):
        assert await stage_repo.list_by_bracket(bracket_dto.id) == []

    async def test_update_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="Original")
        )
        updated = await stage_repo.update(StageUpdate(id=created.id, format=StageFormat.SWISS, name="Updated"))
        assert updated.id == created.id
        assert updated.name == "Updated"
        assert updated.format == StageFormat.SWISS

    async def test_delete_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="Delete Me")
        )
        assert await stage_repo.delete(created.id) is True
        assert await stage_repo.get(created.id) is None

    async def test_list_stages_different_brackets_isolated(self, stage_repo, bracket_repo, event_dto):
        bracket1 = await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        bracket2 = await bracket_repo.create(BracketCreate(event_id=event_dto.id))

        await stage_repo.create(StageCreate(stage_index=1, bracket_id=bracket1.id, format=StageFormat.ROUND_ROBIN, name="Bracket1 Stage"))
        await stage_repo.create(StageCreate(stage_index=1, bracket_id=bracket2.id, format=StageFormat.SWISS, name="Bracket2 Stage"))

        assert len(await stage_repo.list_by_bracket(bracket1.id)) == 1
        assert len(await stage_repo.list_by_bracket(bracket2.id)) == 1

    async def test_create_stages_with_different_formats(self, stage_repo, bracket_dto):
        rr_stage = await stage_repo.create(
            StageCreate(stage_index=1, bracket_id=bracket_dto.id, format=StageFormat.ROUND_ROBIN, name="RR Stage")
        )
        swiss_stage = await stage_repo.create(
            StageCreate(stage_index=2, bracket_id=bracket_dto.id, format=StageFormat.SWISS, name="Swiss Stage")
        )
        assert rr_stage.format == StageFormat.ROUND_ROBIN
        assert swiss_stage.format == StageFormat.SWISS

