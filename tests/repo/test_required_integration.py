import uuid
import pytest

from src.core.models.required_integration import RequiredIntegrationCreate


pytestmark = pytest.mark.asyncio


class TestRequiredIntegrationRepository:
    async def test_create_required_integration(self, required_integration_repo, event_dto):
        created = await required_integration_repo.create(
            RequiredIntegrationCreate(event_id=event_dto.id, name="twitch")
        )
        assert created.id is not None
        assert created.event_id == event_dto.id
        assert created.name == "twitch"

    async def test_get_required_integration_by_id(self, required_integration_repo, event_dto):
        created = await required_integration_repo.create(
            RequiredIntegrationCreate(event_id=event_dto.id, name="github")
        )
        fetched = await required_integration_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "github"

    async def test_get_non_existent_required_integration_returns_none(self, required_integration_repo):
        fetched = await required_integration_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_required_integration_with_relations(self, required_integration_repo, event_dto):
        created = await required_integration_repo.create(
            RequiredIntegrationCreate(event_id=event_dto.id, name="twitch")
        )
        fetched = await required_integration_repo.get(created.id, load_event=True)
        assert fetched is not None
        assert fetched.event is not None
        assert fetched.event.id == event_dto.id

    async def test_list_required_integrations_by_event(self, required_integration_repo, event_dto):
        for i, name in enumerate(["twitch", "discord", "github"]):
            await required_integration_repo.create(
                RequiredIntegrationCreate(event_id=event_dto.id, name=name)
            )
        listed = await required_integration_repo.list_by_event(event_dto.id)
        assert len(listed) == 3
        assert all(i.event_id == event_dto.id for i in listed)

    async def test_exists_required_integration(self, required_integration_repo, event_dto):
        created = await required_integration_repo.create(
            RequiredIntegrationCreate(event_id=event_dto.id, name="twitch")
        )
        assert await required_integration_repo.exists(created.id) is True

    async def test_exists_non_existent_required_integration_returns_false(self, required_integration_repo):
        assert await required_integration_repo.exists(uuid.uuid4()) is False

    async def test_delete_required_integration(self, required_integration_repo, event_dto):
        created = await required_integration_repo.create(
            RequiredIntegrationCreate(event_id=event_dto.id, name="twitch")
        )
        assert await required_integration_repo.delete(created.id) is True
        fetched = await required_integration_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_required_integration_returns_false(self, required_integration_repo):
        assert await required_integration_repo.delete(uuid.uuid4()) is False
