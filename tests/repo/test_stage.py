import uuid

import pytest

from src.core.models.bracket import BracketCreate
from src.core.models.stage import Stage, StageCreate, StageFormat, StageUpdate
from src.infra.postgre.exceptions import IntegrityForeignException

pytestmark = pytest.mark.asyncio


class TestStageRepository:
    async def test_create_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.ROUND_ROBIN,
                name="Stage 1",
            )
        )

        assert isinstance(created, Stage)
        assert created.bracket_id == bracket_dto.id
        assert created.stage_index == 1
        assert created.format == StageFormat.ROUND_ROBIN

    async def test_create_stage_foreign_key_violation(self, stage_repo):
        with pytest.raises(IntegrityForeignException):
            await stage_repo.create(
                StageCreate(
                    stage_index=1,
                    bracket_id=uuid.uuid4(),
                    format=StageFormat.ROUND_ROBIN,
                    name="Invalid",
                )
            )

    async def test_get_stage_by_id(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.SINGLE_ELIMINATION,
                name="Lookup",
            )
        )
        retrieved = await stage_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Lookup"

    async def test_get_stage_with_groups_relation(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.ROUND_ROBIN,
                name="Groups",
            )
        )
        retrieved = await stage_repo.get(created.id, load_groups=True)

        assert retrieved is not None
        assert retrieved.groups == []

    async def test_get_stage_with_settings_relation(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.SWISS,
                name="Settings",
            )
        )
        retrieved = await stage_repo.get(created.id, load_settings=True)

        assert retrieved is not None
        assert retrieved.round_robin_settings is None
        assert retrieved.swiss_settings is None

    async def test_list_by_bracket(self, stage_repo, bracket_dto):
        for i in range(3):
            await stage_repo.create(
                StageCreate(
                    stage_index=i + 1,
                    bracket_id=bracket_dto.id,
                    format=StageFormat.ROUND_ROBIN,
                    name=f"Stage {i + 1}",
                )
            )

        stages = await stage_repo.list_by_bracket(bracket_dto.id)

        assert len(stages) == 3
        assert all(stage.bracket_id == bracket_dto.id for stage in stages)

    async def test_list_by_bracket_with_pagination(self, stage_repo, bracket_dto):
        for i in range(5):
            await stage_repo.create(
                StageCreate(
                    stage_index=i + 1,
                    bracket_id=bracket_dto.id,
                    format=StageFormat.ROUND_ROBIN,
                    name=f"Stage {i + 1}",
                )
            )

        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=0, limit=2)) == 2
        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=2, limit=2)) == 2
        assert len(await stage_repo.list_by_bracket(bracket_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_bracket_empty_when_no_stages(self, stage_repo, bracket_dto):
        assert await stage_repo.list_by_bracket(bracket_dto.id) == []

    async def test_update_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.ROUND_ROBIN,
                name="Original",
            )
        )
        updated = await stage_repo.update(
            StageUpdate(id=created.id, format=StageFormat.SWISS, name="Updated")
        )

        assert updated.id == created.id
        assert updated.name == "Updated"
        assert updated.format == StageFormat.SWISS

    async def test_delete_stage(self, stage_repo, bracket_dto):
        created = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.ROUND_ROBIN,
                name="Delete Me",
            )
        )

        assert await stage_repo.delete(created.id) is True
        assert await stage_repo.get(created.id) is None

    async def test_list_stages_different_brackets_isolated(self, stage_repo, bracket_repo, event_dto):
        bracket1 = await bracket_repo.create(BracketCreate(event_id=event_dto.id))
        bracket2 = await bracket_repo.create(BracketCreate(event_id=event_dto.id))

        await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket1.id,
                format=StageFormat.ROUND_ROBIN,
                name="Bracket1 Stage",
            )
        )
        await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket2.id,
                format=StageFormat.SWISS,
                name="Bracket2 Stage",
            )
        )

        assert len(await stage_repo.list_by_bracket(bracket1.id)) == 1
        assert len(await stage_repo.list_by_bracket(bracket2.id)) == 1

    async def test_create_stages_with_different_formats(self, stage_repo, bracket_dto):
        rr_stage = await stage_repo.create(
            StageCreate(
                stage_index=1,
                bracket_id=bracket_dto.id,
                format=StageFormat.ROUND_ROBIN,
                name="RR Stage",
            )
        )
        swiss_stage = await stage_repo.create(
            StageCreate(
                stage_index=2,
                bracket_id=bracket_dto.id,
                format=StageFormat.SWISS,
                name="Swiss Stage",
            )
        )

        assert rr_stage.format == StageFormat.ROUND_ROBIN
        assert swiss_stage.format == StageFormat.SWISS
