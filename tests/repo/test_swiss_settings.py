import uuid
import pytest

from src.core.models.swiss_settings import SwissSettingsCreate


pytestmark = pytest.mark.asyncio


class TestSwissSettingsRepository:
    async def test_create_swiss_settings(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        assert created.id is not None
        assert created.stage_id == swiss_stage_dto.id
        assert created.score_per_win == 3
        assert created.score_per_draw == 1
        assert created.score_per_bye == 3

    async def test_get_swiss_settings_by_id(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        fetched = await swiss_settings_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    async def test_get_non_existent_swiss_settings_returns_none(self, swiss_settings_repo):
        fetched = await swiss_settings_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_swiss_settings_by_stage_id(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        fetched = await swiss_settings_repo.get_by_stage_id(swiss_stage_dto.id)
        assert fetched is not None
        assert fetched.stage_id == swiss_stage_dto.id

    async def test_get_swiss_settings_by_stage_id_with_relations(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        fetched = await swiss_settings_repo.get_by_stage_id(swiss_stage_dto.id, load_stage=True)
        assert fetched is not None
        assert fetched.stage is not None
        assert fetched.stage.id == swiss_stage_dto.id

    async def test_get_by_non_existent_stage_id_returns_none(self, swiss_settings_repo):
        fetched = await swiss_settings_repo.get_by_stage_id(uuid.uuid4())
        assert fetched is None

    async def test_exists_swiss_settings(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        assert await swiss_settings_repo.exists(created.id) is True

    async def test_exists_non_existent_swiss_settings_returns_false(self, swiss_settings_repo):
        assert await swiss_settings_repo.exists(uuid.uuid4()) is False

    async def test_delete_swiss_settings_by_stage(self, swiss_settings_repo, swiss_stage_dto):
        created = await swiss_settings_repo.create(
            SwissSettingsCreate(
                stage_id=swiss_stage_dto.id,
                score_per_win=3,
                score_per_draw=1,
                score_per_bye=3,
            )
        )
        assert await swiss_settings_repo.exists(created.id) is True
        await swiss_settings_repo.delete_by_stage(swiss_stage_dto.id)
        assert await swiss_settings_repo.get_by_stage_id(swiss_stage_dto.id) is None
        assert await swiss_settings_repo.exists(created.id) is False
