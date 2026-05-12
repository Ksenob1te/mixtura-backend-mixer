import uuid

import pytest

from src.core.models.draft import Draft, DraftCreate, DraftStatus, DraftUpdate
from src.core.models.event import Event, EventCreate, EventMatchType, TeamFormation
from src.infra.postgre.repo.draft import DraftRepository
from src.infra.postgre.repo.event import EventRepository

pytestmark = pytest.mark.asyncio


class TestDraftRepository:
    async def test_create_draft(self, draft_repo: DraftRepository, event_dto: Event):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))

        assert isinstance(created, Draft)
        assert created.event_id == event_dto.id
        assert created.status == DraftStatus.OPEN

    async def test_create_draft_foreign_key_violation(self, draft_repo: DraftRepository):
        with pytest.raises(Exception):
            await draft_repo.create(DraftCreate(event_id=uuid.uuid4()))

    async def test_get_draft_by_id(self, draft_repo: DraftRepository, event_dto: Event):
        created = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        retrieved = await draft_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.event_id == event_dto.id
        assert retrieved.status == DraftStatus.OPEN

    async def test_get_non_existent_draft_returns_none(self, draft_repo: DraftRepository):
        assert await draft_repo.get(uuid.uuid4()) is None

    async def test_get_draft_with_drafted_players_relation(
            self,
            draft_repo: DraftRepository,
            draft_dto: Draft,
    ):
        retrieved = await draft_repo.get(draft_dto.id, load_drafted_players=True)

        assert retrieved is not None
        assert retrieved.drafted_players == []

    async def test_list_by_event(self, draft_repo: DraftRepository, event_dto: Event):
        for _ in range(3):
            await draft_repo.create(DraftCreate(event_id=event_dto.id))

        drafts = await draft_repo.list_by_event(event_dto.id)

        assert len(drafts) == 3
        assert all(draft.event_id == event_dto.id for draft in drafts)

    async def test_list_by_event_with_pagination(self, draft_repo: DraftRepository, event_dto: Event):
        for _ in range(5):
            await draft_repo.create(DraftCreate(event_id=event_dto.id))

        assert len(await draft_repo.list_by_event(event_dto.id, offset=0, limit=2)) == 2
        assert len(await draft_repo.list_by_event(event_dto.id, offset=2, limit=2)) == 2
        assert len(await draft_repo.list_by_event(event_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_event_empty_when_no_drafts(self, draft_repo: DraftRepository, event_dto: Event):
        assert await draft_repo.list_by_event(event_dto.id) == []

    async def test_update_draft(self, draft_repo: DraftRepository, draft_dto: Draft):
        updated = await draft_repo.update(
            DraftUpdate(id=draft_dto.id, status=DraftStatus.BALANCE_REQUESTED)
        )

        assert updated.id == draft_dto.id
        assert updated.status == DraftStatus.BALANCE_REQUESTED

    async def test_delete_draft(self, draft_repo: DraftRepository, draft_dto: Draft):
        assert await draft_repo.delete(draft_dto.id) is True
        assert await draft_repo.get(draft_dto.id) is None

    async def test_delete_non_existent_draft_returns_false(self, draft_repo: DraftRepository):
        assert await draft_repo.delete(uuid.uuid4()) is False

    async def test_list_drafts_different_events_isolated(
            self,
            draft_repo: DraftRepository,
            event_repo: EventRepository,
            server_id,
    ):
        event1 = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event 1",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
            )
        )
        event2 = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event 2",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
            )
        )

        await draft_repo.create(DraftCreate(event_id=event1.id))
        await draft_repo.create(DraftCreate(event_id=event2.id))

        assert len(await draft_repo.list_by_event(event1.id)) == 1
        assert len(await draft_repo.list_by_event(event2.id)) == 1
