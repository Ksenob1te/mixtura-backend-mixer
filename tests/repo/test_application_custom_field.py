import uuid
import pytest

from src.core.models.application_custom_field import ApplicationCustomFieldCreate, ApplicationCustomFieldUpdate


pytestmark = pytest.mark.asyncio


class TestApplicationCustomFieldRepository:
    async def test_create_application_custom_field(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Steam", is_private=False, is_required=True)
        )
        assert created.id is not None
        assert created.event_id == event_dto.id
        assert created.name == "Steam"
        assert created.is_private is False
        assert created.is_required is True

    async def test_get_application_custom_field_by_id(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Steam", is_private=False, is_required=True)
        )
        fetched = await application_custom_field_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Steam"

    async def test_get_non_existent_application_custom_field_returns_none(self, application_custom_field_repo):
        fetched = await application_custom_field_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_update_application_custom_field_name(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Steam", is_private=False, is_required=True)
        )
        updated = await application_custom_field_repo.update(
            ApplicationCustomFieldUpdate(id=created.id, name="Steam ID")
        )
        assert updated.name == "Steam ID"
        assert updated.is_private is False

    async def test_update_application_custom_field_privacy(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Email", is_private=False, is_required=False)
        )
        updated = await application_custom_field_repo.update(
            ApplicationCustomFieldUpdate(id=created.id, is_private=True)
        )
        assert updated.is_private is True
        assert updated.name == "Email"

    async def test_list_application_custom_fields_by_event(self, application_custom_field_repo, event_dto):
        for i in range(3):
            await application_custom_field_repo.create(
                ApplicationCustomFieldCreate(
                    event_id=event_dto.id,
                    name=f"Field {i}",
                    is_private=i % 2 == 0,
                    is_required=i % 2 == 1
                )
            )
        listed = await application_custom_field_repo.list_by_event(event_dto.id)
        assert len(listed) == 3
        assert all(f.event_id == event_dto.id for f in listed)

    async def test_exists_application_custom_field(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Steam", is_private=False, is_required=True)
        )
        assert await application_custom_field_repo.exists(created.id) is True

    async def test_exists_non_existent_application_custom_field_returns_false(self, application_custom_field_repo):
        assert await application_custom_field_repo.exists(uuid.uuid4()) is False

    async def test_delete_application_custom_field(self, application_custom_field_repo, event_dto):
        created = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(event_id=event_dto.id, name="Steam", is_private=False, is_required=True)
        )
        assert await application_custom_field_repo.delete(created.id) is True
        fetched = await application_custom_field_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_application_custom_field_returns_false(self, application_custom_field_repo):
        assert await application_custom_field_repo.delete(uuid.uuid4()) is False



