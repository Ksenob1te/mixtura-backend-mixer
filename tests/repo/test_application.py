import uuid
import pytest

from src.core.models.application import ApplicationCreate, ApplicationUpdate, ApplicationStatus
from src.infra.postgre.exceptions import IntegrityForeignException

pytestmark = pytest.mark.asyncio


class TestApplicationRepository:
    async def test_create_and_get_application(self, application_repo, event_dto):
        member_id = uuid.uuid4()
        app_create = ApplicationCreate(
            event_id=event_dto.id,
            member_id=member_id,
            is_approved=False,
            status=ApplicationStatus.PENDING
        )

        # Act
        app = await application_repo.create(app_create)
        fetched_app = await application_repo.get(app.id)

        # Assert
        assert app.id is not None
        assert app.event_id == event_dto.id
        assert fetched_app is not None
        assert fetched_app.id == app.id
        assert fetched_app.status == ApplicationStatus.PENDING

    async def test_create_application_with_approved_status(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id,
            member_id=uuid.uuid4(),
            is_approved=True,
            status=ApplicationStatus.APPROVED
        ))
        assert app.is_approved is True
        assert app.status == ApplicationStatus.APPROVED

    async def test_create_application_foreign_key_violation(self, application_repo):
        invalid_event_id = uuid.uuid4()
        app_create = ApplicationCreate(
            event_id=invalid_event_id,
            member_id=uuid.uuid4(),
            is_approved=False,
            status=ApplicationStatus.PENDING
        )
        with pytest.raises(IntegrityForeignException):
            await application_repo.create(app_create)

    async def test_get_application_by_id(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))
        fetched_app = await application_repo.get(app.id)
        assert fetched_app is not None
        assert fetched_app.id == app.id
        assert fetched_app.status == ApplicationStatus.PENDING

    async def test_get_non_existent_application_returns_none(self, application_repo):
        fetched = await application_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_application_with_relations(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        fetched = await application_repo.get(app.id, load_filled_fields=True, load_integrations=True,
                                             load_event_player=True)
        assert fetched is not None
        assert fetched.filled_fields == []
        assert fetched.integrations == []
        assert fetched.event_player is None

    async def test_update_application_status(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        app_update = ApplicationUpdate(
            id=app.id,
            status=ApplicationStatus.APPROVED,
            is_approved=True
        )

        updated_app = await application_repo.update(app_update)
        assert updated_app.status == ApplicationStatus.APPROVED
        assert updated_app.is_approved is True

        fetched_app = await application_repo.get(app.id)
        assert fetched_app.status == ApplicationStatus.APPROVED

    async def test_update_application_to_rejected(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        updated_app = await application_repo.update(ApplicationUpdate(
            id=app.id,
            status=ApplicationStatus.REJECTED
        ))
        assert updated_app.status == ApplicationStatus.REJECTED

    async def test_get_application_by_event_and_member(self, application_repo, event_dto):
        member_id = uuid.uuid4()
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=member_id, status=ApplicationStatus.PENDING
        ))

        fetched_by_em = await application_repo.get_by_event_and_member(event_dto.id, member_id)
        assert fetched_by_em is not None
        assert fetched_by_em.id == app.id

    async def test_get_application_by_event_and_member_not_found(self, application_repo, event_dto):
        not_found = await application_repo.get_by_event_and_member(event_dto.id, uuid.uuid4())
        assert not_found is None

    async def test_list_applications_by_event(self, application_repo, event_dto):
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.REJECTED))

        list_apps = await application_repo.list_by_event(event_dto.id, offset=0, limit=10)
        assert len(list_apps) == 3

    async def test_list_applications_by_event_with_status_filter(self, application_repo, event_dto):
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING))

        approved_apps = await application_repo.list_by_event(event_dto.id, offset=0, limit=10,
                                                             status=ApplicationStatus.APPROVED)
        assert len(approved_apps) == 2

    async def test_list_applications_with_pagination(self, application_repo, event_dto):
        for _ in range(5):
            await application_repo.create(
                ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING))

        page1 = await application_repo.list_by_event(event_dto.id, offset=0, limit=2)
        page2 = await application_repo.list_by_event(event_dto.id, offset=2, limit=2)
        page3 = await application_repo.list_by_event(event_dto.id, offset=4, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_list_applications_by_event_empty(self, application_repo, event_dto):
        empty_list = await application_repo.list_by_event(event_dto.id, offset=0, limit=10)
        assert len(empty_list) == 0

    async def test_count_applications_by_event_and_status(self, application_repo, event_dto):
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await application_repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING))

        count_approved = await application_repo.count_by_event_and_status(event_dto.id, ApplicationStatus.APPROVED)
        assert count_approved == 2

    async def test_count_applications_by_non_existent_event(self, application_repo):
        empty_count = await application_repo.count_by_event_and_status(uuid.uuid4(), ApplicationStatus.PENDING)
        assert empty_count == 0

    async def test_delete_application(self, application_repo, event_dto):
        app = await application_repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        delete_success = await application_repo.delete(app.id)
        assert delete_success is True

        fetched_app = await application_repo.get(app.id)
        assert fetched_app is None

    async def test_delete_non_existent_application_returns_false(self, application_repo):
        delete_fail = await application_repo.delete(uuid.uuid4())
        assert delete_fail is False
