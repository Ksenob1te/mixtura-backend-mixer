import uuid
import pytest

from src.core.models.stage_group import StageGroupCreate
from src.core.models.match import MatchCreate


pytestmark = pytest.mark.asyncio


class TestStageGroupRepository:
    async def test_create_stage_group(self, stage_group_repo, round_robin_stage_dto):
        created = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group A"))
        assert created.id is not None
        assert created.stage_id == round_robin_stage_dto.id
        assert created.name == "Group A"

    async def test_create_stage_group_different_names(self, stage_group_repo, round_robin_stage_dto):
        group_b = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group B"))
        group_c = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group C"))
        assert group_b.name == "Group B"
        assert group_c.name == "Group C"

    async def test_get_stage_group_by_id(self, stage_group_repo, round_robin_stage_dto):
        created = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group A"))
        fetched = await stage_group_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Group A"

    async def test_get_non_existent_stage_group_returns_none(self, stage_group_repo):
        fetched = await stage_group_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_stage_group_with_matches_relation(self, stage_group_repo, round_robin_stage_dto, match_repo):
        group = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group B"))
        match1 = await match_repo.create(MatchCreate(group_id=group.id, match_index=1))
        match2 = await match_repo.create(MatchCreate(group_id=group.id, match_index=2))

        fetched = await stage_group_repo.get(group.id, load_matches=True)
        assert fetched is not None
        assert len(fetched.matches) == 2
        assert {m.id for m in fetched.matches} == {match1.id, match2.id}

    async def test_list_stage_groups_by_stage(self, stage_group_repo, round_robin_stage_dto):
        group_a = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group A"))
        group_b = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group B"))
        group_c = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group C"))

        listed = await stage_group_repo.list_by_stage(round_robin_stage_dto.id)
        assert len(listed) == 3
        assert {g.id for g in listed} == {group_a.id, group_b.id, group_c.id}

    async def test_list_stage_groups_by_stage_multiple(self, stage_group_repo, round_robin_stage_dto):
        for i in range(5):
            await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name=f"Group {i}"))

        listed = await stage_group_repo.list_by_stage(round_robin_stage_dto.id)
        assert len(listed) == 5

    async def test_exists_stage_group(self, stage_group_repo, round_robin_stage_dto):
        created = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group A"))
        assert await stage_group_repo.exists(created.id) is True

    async def test_exists_non_existent_stage_group_returns_false(self, stage_group_repo):
        assert await stage_group_repo.exists(uuid.uuid4()) is False

    async def test_delete_stage_group_with_matches(self, stage_group_repo, round_robin_stage_dto, match_repo):
        group = await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group B"))
        match = await match_repo.create(MatchCreate(group_id=group.id, match_index=5))

        assert await stage_group_repo.exists(group.id) is True
        assert await stage_group_repo.delete(group.id) is True
        assert await stage_group_repo.get(group.id) is None
        assert await stage_group_repo.exists(group.id) is False

    async def test_delete_non_existent_stage_group_returns_false(self, stage_group_repo):
        assert await stage_group_repo.delete(uuid.uuid4()) is False

