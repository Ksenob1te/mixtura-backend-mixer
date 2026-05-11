import uuid
import pytest

from src.core.models.drafted_player import DraftedPlayerCreate


pytestmark = pytest.mark.asyncio


class TestDraftedPlayerRepository:
    async def test_create_drafted_player(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=True)
        )
        assert created.id is not None
        assert created.draft_id == draft_dto.id
        assert created.event_player_id == event_player_dto.id
        assert created.is_captain is True

    async def test_create_drafted_player_not_captain(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=False)
        )
        assert created.is_captain is False

    async def test_get_drafted_player_by_id(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=False)
        )
        fetched = await drafted_player_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.draft_id == draft_dto.id

    async def test_get_non_existent_drafted_player_returns_none(self, drafted_player_repo):
        fetched = await drafted_player_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_drafted_player_with_relations(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=True)
        )
        fetched = await drafted_player_repo.get(created.id, load_draft=True, load_player=True)
        assert fetched is not None
        assert fetched.draft is not None
        assert fetched.draft.id == draft_dto.id
        assert fetched.event_player is not None
        assert fetched.event_player.id == event_player_dto.id

    async def test_list_drafted_players_by_draft(self, drafted_player_repo, draft_dto, player_repo, event_dto):
        for i in range(3):
            player = await player_repo.create(
                __import__('src.core.models.event_player', fromlist=['EventPlayerCreate']).EventPlayerCreate(
                    event_id=event_dto.id, member_id=uuid.uuid4()
                )
            )
            await drafted_player_repo.create(
                DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=player.id, is_captain=i == 0)
            )
        listed = await drafted_player_repo.list_by_draft(draft_dto.id)
        assert len(listed) == 3
        assert all(p.draft_id == draft_dto.id for p in listed)

    async def test_exists_drafted_player(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=False)
        )
        assert await drafted_player_repo.exists(created.id) is True

    async def test_exists_non_existent_drafted_player_returns_false(self, drafted_player_repo):
        assert await drafted_player_repo.exists(uuid.uuid4()) is False

    async def test_delete_drafted_player(self, drafted_player_repo, draft_dto, event_player_dto):
        created = await drafted_player_repo.create(
            DraftedPlayerCreate(draft_id=draft_dto.id, event_player_id=event_player_dto.id, is_captain=True)
        )
        assert await drafted_player_repo.delete(created.id) is True
        fetched = await drafted_player_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_drafted_player_returns_false(self, drafted_player_repo):
        assert await drafted_player_repo.delete(uuid.uuid4()) is False
