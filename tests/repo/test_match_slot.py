import uuid
import pytest

from src.core.models.match_slot import MatchSlotCreate, MatchSlotSourceType
from src.core.models.match_score import MatchScoreCreate


pytestmark = pytest.mark.asyncio


class TestMatchSlotRepository:
    async def test_create_match_slot(self, match_slot_repo, match_dto):
        created = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        assert created.id is not None
        assert created.match_id == match_dto.id
        assert created.slot_num == 1
        assert created.source_type == MatchSlotSourceType.MANUAL

    async def test_create_match_slot_with_generated_source_type(self, match_slot_repo, match_dto):
        created = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=2, source_type=MatchSlotSourceType.MANUAL)
        )
        assert created.source_type == MatchSlotSourceType.MANUAL

    async def test_get_match_slot_by_id(self, match_slot_repo, match_dto):
        created = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        fetched = await match_slot_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.slot_num == 1

    async def test_get_non_existent_match_slot_returns_none(self, match_slot_repo):
        fetched = await match_slot_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_match_slot_with_score_relation(self, match_slot_repo, match_score_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=10))

        fetched = await match_slot_repo.get(slot.id, load_score=True)
        assert fetched is not None
        assert fetched.score is not None
        assert fetched.score.team_id == team_dto.id
        assert fetched.score.score == 10

    async def test_list_match_slots_by_match_in_order(self, match_slot_repo, match_dto):
        slot3 = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=3, source_type=MatchSlotSourceType.MANUAL)
        )
        slot1 = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        slot2 = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=2, source_type=MatchSlotSourceType.MANUAL)
        )

        listed = await match_slot_repo.list_by_match(match_dto.id)
        assert len(listed) == 3
        assert [slot.slot_num for slot in listed] == [1, 2, 3]
        assert {slot.id for slot in listed} == {slot1.id, slot2.id, slot3.id}

    async def test_exists_match_slot(self, match_slot_repo, match_dto):
        created = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        assert await match_slot_repo.exists(created.id) is True

    async def test_exists_non_existent_match_slot_returns_false(self, match_slot_repo):
        assert await match_slot_repo.exists(uuid.uuid4()) is False

    async def test_delete_match_slot(self, match_slot_repo, match_dto):
        created = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        assert await match_slot_repo.delete(created.id) is True
        fetched = await match_slot_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_match_slot_returns_false(self, match_slot_repo):
        assert await match_slot_repo.delete(uuid.uuid4()) is False

