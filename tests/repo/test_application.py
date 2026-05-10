import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models.application import ApplicationCreate, ApplicationUpdate, ApplicationStatus
from src.core.models.event import Event, EventCreate, EventMatchType, TeamFormation
from src.infra.postgre.exceptions import IntegrityForeignException
from src.infra.postgre.repo.application import ApplicationRepository
from src.infra.postgre.repo.event import EventRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
def repo(async_session: AsyncSession) -> ApplicationRepository:
    return ApplicationRepository(async_session)


@pytest.fixture
def event_repo(async_session: AsyncSession) -> EventRepository:
    return EventRepository(async_session)


@pytest.fixture
async def event_dto(event_repo: EventRepository) -> Event:
    server_id = uuid.uuid4()
    return await event_repo.create(EventCreate(
        name="Test Event",
        match_type=EventMatchType.SINGLE,
        use_application=True,
        is_public=True,
        team_size=5,
        team_formation=TeamFormation.BALANCE,
        allow_multiple_drafts=False,
        server_id=server_id
    ))


class TestApplicationRepository:
    async def test_create_and_get_application(self, repo: ApplicationRepository, event_dto: Event):
        member_id = uuid.uuid4()
        app_create = ApplicationCreate(
            event_id=event_dto.id,
            member_id=member_id,
            is_approved=False,
            status=ApplicationStatus.PENDING
        )

        # Act
        app = await repo.create(app_create)
        fetched_app = await repo.get(app.id)

        # Assert
        assert app.id is not None
        assert app.event_id == event_dto.id
        assert fetched_app is not None
        assert fetched_app.id == app.id
        assert fetched_app.status == ApplicationStatus.PENDING

    async def test_create_integrity_error(self, repo: ApplicationRepository):
        # Act & Assert
        invalid_event_id = uuid.uuid4()
        app_create = ApplicationCreate(
            event_id=invalid_event_id,
            member_id=uuid.uuid4(),
            is_approved=False,
            status=ApplicationStatus.PENDING
        )
        with pytest.raises(IntegrityForeignException):
            await repo.create(app_create)

    async def test_get_non_existent_application(self, repo: ApplicationRepository):
        fetched = await repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_with_relations(self, repo: ApplicationRepository, event_dto: Event):
        app = await repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        fetched = await repo.get(app.id, load_filled_fields=True, load_integrations=True, load_event_player=True)
        assert fetched is not None
        assert fetched.filled_fields == []
        assert fetched.integrations == []
        assert fetched.event_player is None

    async def test_update_application(self, repo: ApplicationRepository, event_dto: Event):
        app = await repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        app_update = ApplicationUpdate(
            id=app.id,
            status=ApplicationStatus.APPROVED,
            is_approved=True
        )

        # Act
        updated_app = await repo.update(app_update)
        fetched_app = await repo.get(app.id)
        assert fetched_app is not None

        # Assert
        assert updated_app.status == ApplicationStatus.APPROVED
        assert updated_app.is_approved is True
        assert fetched_app.status == ApplicationStatus.APPROVED
        assert fetched_app.is_approved is True

    async def test_get_by_event_and_member(self, repo: ApplicationRepository, event_dto: Event):
        member_id = uuid.uuid4()
        app = await repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=member_id, status=ApplicationStatus.PENDING
        ))

        # Act
        fetched_by_em = await repo.get_by_event_and_member(event_dto.id, member_id)
        not_found = await repo.get_by_event_and_member(event_dto.id, uuid.uuid4())

        # Assert
        assert fetched_by_em is not None
        assert fetched_by_em.id == app.id
        assert not_found is None

    async def test_list_and_count_by_event(self, repo: ApplicationRepository, event_dto: Event):
        # Create multiple apps
        await repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.APPROVED))
        await repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING))
        await repo.create(
            ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.REJECTED))

        # Act
        list_apps = await repo.list_by_event(event_dto.id, offset=0, limit=10)
        approved_apps = await repo.list_by_event(event_dto.id, offset=0, limit=10, status=ApplicationStatus.APPROVED)
        count_approved = await repo.count_by_event_and_status(event_dto.id, ApplicationStatus.APPROVED)

        # Assert
        assert len(list_apps) == 3
        assert len(approved_apps) == 1
        assert count_approved == 1

        # Test sorting and limits
        sorted_apps_asc = await repo.list_by_event(event_dto.id, offset=0, limit=2, sort_order="asc", sort_by="status")
        assert len(sorted_apps_asc) == 2

        empty_list = await repo.list_by_event(uuid.uuid4(), offset=0, limit=10)
        assert len(empty_list) == 0

        empty_count = await repo.count_by_event_and_status(uuid.uuid4(), ApplicationStatus.PENDING)
        assert empty_count == 0

    async def test_delete_application(self, repo: ApplicationRepository, event_dto: Event):
        app = await repo.create(ApplicationCreate(
            event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING
        ))

        # Act
        delete_success = await repo.delete(app.id)
        delete_fail = await repo.delete(uuid.uuid4())
        fetched_app = await repo.get(app.id)

        # Assert
        assert delete_success is True
        assert delete_fail is False
        assert fetched_app is None
