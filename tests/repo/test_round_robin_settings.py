import uuid
import pytest

from src.core.models.round_robin_settings import RoundRobinSettingsCreate


pytestmark = pytest.mark.asyncio


class TestRoundRobinSettingsRepository:
    async def test_create_round_robin_settings(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        assert created.id is not None
        assert created.stage_id == round_robin_stage_dto.id
        assert created.meetings_per_pair == 2
        assert created.score_per_win == 3
        assert created.score_per_draw == 1

    async def test_create_round_robin_settings_different_points(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=1,
                score_system="points",
                score_per_win=5,
                score_per_draw=2,
            )
        )
        assert created.score_per_win == 5
        assert created.score_per_draw == 2

    async def test_get_round_robin_settings_by_id(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        fetched = await round_robin_settings_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    async def test_get_non_existent_round_robin_settings_returns_none(self, round_robin_settings_repo):
        fetched = await round_robin_settings_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_round_robin_settings_by_stage_id(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        fetched = await round_robin_settings_repo.get_by_stage_id(round_robin_stage_dto.id)
        assert fetched is not None
        assert fetched.stage_id == round_robin_stage_dto.id

    async def test_get_round_robin_settings_by_stage_id_with_relations(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        fetched = await round_robin_settings_repo.get_by_stage_id(round_robin_stage_dto.id, load_stage=True)
        assert fetched is not None
        assert fetched.stage is not None
        assert fetched.stage.id == round_robin_stage_dto.id

    async def test_get_by_non_existent_stage_id_returns_none(self, round_robin_settings_repo):
        fetched = await round_robin_settings_repo.get_by_stage_id(uuid.uuid4())
        assert fetched is None

    async def test_exists_round_robin_settings(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        assert await round_robin_settings_repo.exists(created.id) is True

    async def test_exists_non_existent_round_robin_settings_returns_false(self, round_robin_settings_repo):
        assert await round_robin_settings_repo.exists(uuid.uuid4()) is False

    async def test_delete_round_robin_settings_by_stage(self, round_robin_settings_repo, round_robin_stage_dto):
        created = await round_robin_settings_repo.create(
            RoundRobinSettingsCreate(
                stage_id=round_robin_stage_dto.id,
                meetings_per_pair=2,
                score_system="points",
                score_per_win=3,
                score_per_draw=1,
            )
        )
        assert await round_robin_settings_repo.exists(created.id) is True
        await round_robin_settings_repo.delete_by_stage(round_robin_stage_dto.id)
        assert await round_robin_settings_repo.get_by_stage_id(round_robin_stage_dto.id) is None
        assert await round_robin_settings_repo.exists(created.id) is False
