import uuid
import pytest

from src.core.models.player_role import PlayerRoleCreate


pytestmark = pytest.mark.asyncio


class TestPlayerRoleRepository:
    async def test_create_player_role(self, player_role_repo, event_player_dto, selected_game_role_dto):
        created = await player_role_repo.create(
            PlayerRoleCreate(
                event_player_id=event_player_dto.id,
                game_role_id=selected_game_role_dto.id,
                priority=2,
            )
        )
        assert created.id is not None
        assert created.event_player_id == event_player_dto.id
        assert created.game_role_id == selected_game_role_dto.id
        assert created.priority == 2

    async def test_get_player_role_by_id(self, player_role_repo, event_player_dto, selected_game_role_dto):
        created = await player_role_repo.create(
            PlayerRoleCreate(
                event_player_id=event_player_dto.id,
                game_role_id=selected_game_role_dto.id,
                priority=1,
            )
        )
        fetched = await player_role_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.priority == 1

    async def test_get_non_existent_player_role_returns_none(self, player_role_repo):
        fetched = await player_role_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_player_role_with_relations(self, player_role_repo, event_player_dto, selected_game_role_dto):
        created = await player_role_repo.create(
            PlayerRoleCreate(
                event_player_id=event_player_dto.id,
                game_role_id=selected_game_role_dto.id,
                priority=2,
            )
        )
        fetched = await player_role_repo.get(created.id, load_player=True, load_game_role=True)
        assert fetched is not None
        assert fetched.event_player is not None
        assert fetched.event_player.id == event_player_dto.id
        assert fetched.game_role is not None
        assert fetched.game_role.id == selected_game_role_dto.id

    async def test_list_player_roles_by_player(self, player_role_repo, player_repo, event_dto, selected_game_role_dto):
        player = await player_repo.create(
            __import__('src.core.models.event_player', fromlist=['EventPlayerCreate']).EventPlayerCreate(
                event_id=event_dto.id, member_id=__import__('uuid', fromlist=['uuid4']).uuid4()
            )
        )
        role1 = await player_role_repo.create(
            PlayerRoleCreate(event_player_id=player.id, game_role_id=selected_game_role_dto.id, priority=1)
        )
        listed = await player_role_repo.list_by_player(player.id)
        assert len(listed) == 1
        assert listed[0].id == role1.id

    async def test_exists_player_role(self, player_role_repo, event_player_dto, selected_game_role_dto):
        created = await player_role_repo.create(
            PlayerRoleCreate(
                event_player_id=event_player_dto.id,
                game_role_id=selected_game_role_dto.id,
                priority=1,
            )
        )
        assert await player_role_repo.exists(created.id) is True

    async def test_exists_non_existent_player_role_returns_false(self, player_role_repo):
        assert await player_role_repo.exists(uuid.uuid4()) is False

    async def test_delete_player_role(self, player_role_repo, event_player_dto, selected_game_role_dto):
        created = await player_role_repo.create(
            PlayerRoleCreate(
                event_player_id=event_player_dto.id,
                game_role_id=selected_game_role_dto.id,
                priority=1,
            )
        )
        assert await player_role_repo.delete(created.id) is True
        fetched = await player_role_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_player_role_returns_false(self, player_role_repo):
        assert await player_role_repo.delete(uuid.uuid4()) is False


