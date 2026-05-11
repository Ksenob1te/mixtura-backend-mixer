import uuid
import pytest

from src.core.models.application_integration import ApplicationIntegrationCreate


pytestmark = pytest.mark.asyncio


class TestApplicationIntegrationRepository:
    async def test_create_application_integration(self, application_integration_repo, application_dto):
        provider_id = uuid.uuid4()
        user_provider_id = uuid.uuid4()
        created = await application_integration_repo.create(
            ApplicationIntegrationCreate(
                application_id=application_dto.id,
                user_provider_id=user_provider_id,
                provider_id=provider_id,
                provider_name="github",
            )
        )
        assert created.id is not None
        assert created.application_id == application_dto.id
        assert created.provider_name == "github"

    async def test_get_application_integration_by_id(self, application_integration_repo, application_dto):
        created = await application_integration_repo.create(
            ApplicationIntegrationCreate(
                application_id=application_dto.id,
                user_provider_id=uuid.uuid4(),
                provider_id=uuid.uuid4(),
                provider_name="twitch",
            )
        )
        fetched = await application_integration_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.provider_name == "twitch"

    async def test_get_non_existent_application_integration_returns_none(self, application_integration_repo):
        fetched = await application_integration_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_application_integration_with_relations(self, application_integration_repo, application_dto):
        created = await application_integration_repo.create(
            ApplicationIntegrationCreate(
                application_id=application_dto.id,
                user_provider_id=uuid.uuid4(),
                provider_id=uuid.uuid4(),
                provider_name="github",
            )
        )
        fetched = await application_integration_repo.get(created.id, load_application=True)
        assert fetched is not None
        assert fetched.application is not None
        assert fetched.application.id == application_dto.id

    async def test_list_application_integrations_by_application(self, application_integration_repo, application_dto):
        for i in range(3):
            await application_integration_repo.create(
                ApplicationIntegrationCreate(
                    application_id=application_dto.id,
                    user_provider_id=uuid.uuid4(),
                    provider_id=uuid.uuid4(),
                    provider_name=f"provider_{i}",
                )
            )
        listed = await application_integration_repo.list_by_application(application_dto.id)
        assert len(listed) == 3
        assert all(i.application_id == application_dto.id for i in listed)

    async def test_exists_application_integration(self, application_integration_repo, application_dto):
        created = await application_integration_repo.create(
            ApplicationIntegrationCreate(
                application_id=application_dto.id,
                user_provider_id=uuid.uuid4(),
                provider_id=uuid.uuid4(),
                provider_name="github",
            )
        )
        assert await application_integration_repo.exists(created.id) is True

    async def test_exists_non_existent_application_integration_returns_false(self, application_integration_repo):
        assert await application_integration_repo.exists(uuid.uuid4()) is False

    async def test_delete_application_integration(self, application_integration_repo, application_dto):
        created = await application_integration_repo.create(
            ApplicationIntegrationCreate(
                application_id=application_dto.id,
                user_provider_id=uuid.uuid4(),
                provider_id=uuid.uuid4(),
                provider_name="github",
            )
        )
        assert await application_integration_repo.delete(created.id) is True
        fetched = await application_integration_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_application_integration_returns_false(self, application_integration_repo):
        assert await application_integration_repo.delete(uuid.uuid4()) is False
