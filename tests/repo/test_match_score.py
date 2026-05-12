import uuid
import pytest

from src.core.models.match_slot import MatchSlotCreate, MatchSlotSourceType
from src.core.models.match_score import MatchScoreCreate, MatchScoreUpdate


pytestmark = pytest.mark.asyncio


class TestMatchScoreRepository:
    async def test_create_match_score(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=0))
        assert created.id is not None
        assert created.slot_id == slot.id
        assert created.team_id == team_dto.id
        assert created.score == 0

    async def test_get_match_score_by_id(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=5))
        fetched = await match_score_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.score == 5

    async def test_get_non_existent_match_score_returns_none(self, match_score_repo):
        fetched = await match_score_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_match_score_with_relations(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=0))

        fetched = await match_score_repo.get(created.id, load_slot=True, load_team=True)
        assert fetched is not None
        assert fetched.slot is not None
        assert fetched.slot.id == slot.id
        assert fetched.team is not None
        assert fetched.team.id == team_dto.id

    async def test_get_match_score_by_slot_id(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=3))

        by_slot = await match_score_repo.get_by_slot_id(slot.id, load_slot=True, load_team=True)
        assert by_slot is not None
        assert by_slot.id == created.id
        assert by_slot.slot is not None
        assert by_slot.team is not None

    async def test_get_by_non_existent_slot_id_returns_none(self, match_score_repo):
        by_slot = await match_score_repo.get_by_slot_id(uuid.uuid4())
        assert by_slot is None

    async def test_update_match_score(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=0))
        updated = await match_score_repo.update(created.id, MatchScoreUpdate(score=7))
        assert updated.score == 7

    async def test_update_match_score_to_zero(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=2, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=10))
        updated = await match_score_repo.update(created.id, MatchScoreUpdate(score=0))
        assert updated.score == 0

    async def test_exists_match_score(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=0))
        assert await match_score_repo.exists(created.id) is True

    async def test_exists_non_existent_match_score_returns_false(self, match_score_repo):
        assert await match_score_repo.exists(uuid.uuid4()) is False

    async def test_delete_match_score(self, match_score_repo, match_slot_repo, match_dto, team_dto):
        slot = await match_slot_repo.create(
            MatchSlotCreate(match_id=match_dto.id, slot_num=1, source_type=MatchSlotSourceType.MANUAL)
        )
        created = await match_score_repo.create(MatchScoreCreate(slot_id=slot.id, team_id=team_dto.id, score=0))
        assert await match_score_repo.delete(created.id) is True
        fetched = await match_score_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_match_score_returns_false(self, match_score_repo):
        assert await match_score_repo.delete(uuid.uuid4()) is False
