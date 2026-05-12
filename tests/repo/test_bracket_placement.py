import uuid
import pytest

from src.core.models.bracket_placement import BracketPlacementCreate

pytestmark = pytest.mark.asyncio


class TestBracketPlacementRepository:
    async def test_create_bracket_placement(self, bracket_placement_repo, bracket_dto, team_dto):
        created = await bracket_placement_repo.create(
            BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=1)
        )
        assert created.id is not None
        assert created.bracket_id == bracket_dto.id
        assert created.team_id == team_dto.id
        assert created.placement == 1

    async def test_get_bracket_placement_by_id(self, bracket_placement_repo, bracket_dto, team_dto):
        created = await bracket_placement_repo.create(
            BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=2)
        )
        fetched = await bracket_placement_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.placement == 2

    async def test_get_non_existent_bracket_placement_returns_none(self, bracket_placement_repo):
        fetched = await bracket_placement_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_bracket_placement_with_relations(self, bracket_placement_repo, bracket_dto, team_dto):
        created = await bracket_placement_repo.create(
            BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=1)
        )
        fetched = await bracket_placement_repo.get(created.id, load_bracket=True)
        assert fetched is not None
        assert fetched.bracket is not None
        assert fetched.bracket.id == bracket_dto.id

    async def test_list_bracket_placements_by_bracket(self, bracket_placement_repo, bracket_dto, team_repo, event_dto):
        for i in range(3):
            team = await team_repo.create(__import__('src.core.models.team', fromlist=['TeamCreate']).TeamCreate(
                event_id=event_dto.id, name=f"Team {i}"
            ))
            await bracket_placement_repo.create(
                BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team.id, placement=i + 1)
            )
        listed = await bracket_placement_repo.list_by_bracket(bracket_dto.id)
        assert len(listed) == 3
        assert all(p.bracket_id == bracket_dto.id for p in listed)

    async def test_exists_bracket_placement(self, bracket_placement_repo, bracket_dto, team_dto):
        created = await bracket_placement_repo.create(
            BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=1)
        )
        assert await bracket_placement_repo.exists(created.id) is True

    async def test_exists_non_existent_bracket_placement_returns_false(self, bracket_placement_repo):
        assert await bracket_placement_repo.exists(uuid.uuid4()) is False

    async def test_delete_bracket_placement(self, bracket_placement_repo, bracket_dto, team_dto):
        created = await bracket_placement_repo.create(
            BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=1)
        )
        assert await bracket_placement_repo.delete(created.id) is True
        fetched = await bracket_placement_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_bracket_placement_returns_false(self, bracket_placement_repo):
        assert await bracket_placement_repo.delete(uuid.uuid4()) is False
