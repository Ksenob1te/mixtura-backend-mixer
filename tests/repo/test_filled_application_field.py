import uuid
import pytest

from src.core.models.filled_application_field import FilledApplicationFieldCreate


pytestmark = pytest.mark.asyncio


class TestFilledApplicationFieldRepository:
    async def test_create_filled_application_field(self, filled_application_field_repo, application_dto, custom_field_dto):
        created = await filled_application_field_repo.create(
            FilledApplicationFieldCreate(
                value="alice#0001",
                custom_field_id=custom_field_dto.id,
                application_id=application_dto.id,
            )
        )
        assert created.id is not None
        assert created.application_id == application_dto.id
        assert created.custom_field_id == custom_field_dto.id
        assert created.value == "alice#0001"

    async def test_get_filled_application_field_by_id(self, filled_application_field_repo, application_dto, custom_field_dto):
        created = await filled_application_field_repo.create(
            FilledApplicationFieldCreate(
                value="bob#0002",
                custom_field_id=custom_field_dto.id,
                application_id=application_dto.id,
            )
        )
        fetched = await filled_application_field_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.value == "bob#0002"

    async def test_get_non_existent_filled_application_field_returns_none(self, filled_application_field_repo):
        fetched = await filled_application_field_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_filled_application_field_with_relations(self, filled_application_field_repo, application_dto, custom_field_dto):
        created = await filled_application_field_repo.create(
            FilledApplicationFieldCreate(
                value="alice#0001",
                custom_field_id=custom_field_dto.id,
                application_id=application_dto.id,
            )
        )
        fetched = await filled_application_field_repo.get(created.id, load_application=True, load_custom_field=True)
        assert fetched is not None
        assert fetched.application is not None
        assert fetched.application.id == application_dto.id
        assert fetched.custom_field is not None
        assert fetched.custom_field.id == custom_field_dto.id

    async def test_list_filled_application_fields_by_application(self, filled_application_field_repo, application_dto, application_custom_field_repo):
        # create unique custom fields so unique constraint (custom_field_id, application_id) is honored
        custom_fields = []
        for i in range(3):
            cf = await application_custom_field_repo.create(
                __import__('src.core.models.application_custom_field', fromlist=['ApplicationCustomFieldCreate']).ApplicationCustomFieldCreate(
                    event_id=application_dto.event_id, name=f"Field {i}", is_private=False, is_required=False
                )
            )
            custom_fields.append(cf)

        for i, cf in enumerate(custom_fields):
            await filled_application_field_repo.create(
                FilledApplicationFieldCreate(
                    value=f"value_{i}",
                    custom_field_id=cf.id,
                    application_id=application_dto.id,
                )
            )

        listed = await filled_application_field_repo.list_by_application(application_dto.id)
        assert len(listed) == 3
        assert all(f.application_id == application_dto.id for f in listed)

    async def test_exists_filled_application_field(self, filled_application_field_repo, application_dto, custom_field_dto):
        created = await filled_application_field_repo.create(
            FilledApplicationFieldCreate(
                value="test#1234",
                custom_field_id=custom_field_dto.id,
                application_id=application_dto.id,
            )
        )
        assert await filled_application_field_repo.exists(created.id) is True

    async def test_exists_non_existent_filled_application_field_returns_false(self, filled_application_field_repo):
        assert await filled_application_field_repo.exists(uuid.uuid4()) is False

    async def test_delete_filled_application_field(self, filled_application_field_repo, application_dto, custom_field_dto):
        created = await filled_application_field_repo.create(
            FilledApplicationFieldCreate(
                value="alice#0001",
                custom_field_id=custom_field_dto.id,
                application_id=application_dto.id,
            )
        )
        assert await filled_application_field_repo.delete(created.id) is True
        fetched = await filled_application_field_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_filled_application_field_returns_false(self, filled_application_field_repo):
        assert await filled_application_field_repo.delete(uuid.uuid4()) is False

