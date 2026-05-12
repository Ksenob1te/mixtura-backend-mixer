from datetime import datetime
import uuid
import pytest

from src.core.models.application_time_settings import ApplicationTimeSettingsCreate, ApplicationTimeSettingsUpdate

pytestmark = pytest.mark.asyncio


class TestApplicationTimeSettingsRepository:
    async def test_create_application_time_settings(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        assert created.id is not None
        assert created.event_id == event_dto.id
        assert created.start_time == datetime(2026, 1, 1, 12, 0, 0)
        assert created.end_time == datetime(2026, 1, 1, 14, 0, 0)

    async def test_get_application_time_settings_by_id(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 2, 1, 10, 0, 0),
                end_time=datetime(2026, 2, 1, 12, 0, 0),
            )
        )
        fetched = await application_time_settings_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    async def test_get_application_time_settings_by_event_id(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        fetched = await application_time_settings_repo.get_by_event_id(event_dto.id)
        assert fetched is not None
        assert fetched.event_id == event_dto.id
        assert fetched.start_time == datetime(2026, 1, 1, 12, 0, 0)

    async def test_get_application_time_settings_by_event_id_with_relations(self, application_time_settings_repo,
                                                                            event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        fetched = await application_time_settings_repo.get_by_event_id(event_dto.id, load_event=True)
        assert fetched is not None
        assert fetched.event is not None
        assert fetched.event.id == event_dto.id

    async def test_get_non_existent_application_time_settings_returns_none(self, application_time_settings_repo):
        fetched = await application_time_settings_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_by_non_existent_event_id_returns_none(self, application_time_settings_repo):
        fetched = await application_time_settings_repo.get_by_event_id(uuid.uuid4())
        assert fetched is None

    async def test_update_application_time_settings_start_time(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        updated = await application_time_settings_repo.update(
            ApplicationTimeSettingsUpdate(id=created.id, start_time=datetime(2026, 1, 1, 13, 0, 0))
        )
        assert updated.start_time == datetime(2026, 1, 1, 13, 0, 0)
        assert updated.end_time == datetime(2026, 1, 1, 14, 0, 0)

    async def test_update_application_time_settings_end_time(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        updated = await application_time_settings_repo.update(
            ApplicationTimeSettingsUpdate(id=created.id, end_time=datetime(2026, 1, 1, 15, 0, 0))
        )
        assert updated.end_time == datetime(2026, 1, 1, 15, 0, 0)

    async def test_exists_application_time_settings(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        assert await application_time_settings_repo.exists(created.id) is True

    async def test_exists_non_existent_application_time_settings_returns_false(self, application_time_settings_repo):
        assert await application_time_settings_repo.exists(uuid.uuid4()) is False

    async def test_delete_application_time_settings_by_event_id(self, application_time_settings_repo, event_dto):
        created = await application_time_settings_repo.create(
            ApplicationTimeSettingsCreate(
                event_id=event_dto.id,
                start_time=datetime(2026, 1, 1, 12, 0, 0),
                end_time=datetime(2026, 1, 1, 14, 0, 0),
            )
        )
        assert await application_time_settings_repo.exists(created.id) is True
        await application_time_settings_repo.delete_by_event_id(event_dto.id)
        assert await application_time_settings_repo.get_by_event_id(event_dto.id) is None
        assert await application_time_settings_repo.exists(created.id) is False
