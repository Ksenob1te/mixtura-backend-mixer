import uuid
import pytest

from src.core.models.selected_game_role import SelectedGameRoleCreate, SelectedGameRoleUpdate
from src.core.models.player_role import PlayerRoleCreate
from src.core.models.team_player import TeamPlayerCreate


pytestmark = pytest.mark.asyncio


class TestSelectedGameRoleRepository:
    async def test_create_selected_game_role(self, selected_game_role_repo, event_dto):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=event_dto.id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )
        assert created.id is not None
        assert created.event_id == event_dto.id
        assert created.override_max_count == 4
        assert created.override_min_count == 1

    async def test_get_selected_game_role_by_id(self, selected_game_role_repo, event_dto):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=event_dto.id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )
        fetched = await selected_game_role_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.event_id == event_dto.id

    async def test_get_non_existent_selected_game_role_returns_none(self, selected_game_role_repo):
        fetched = await selected_game_role_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_selected_game_role_with_relations(
        self,
        selected_game_role_repo,
        player_role_repo,
        team_player_repo,
        event_player_dto,
        team_dto,
    ):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=team_dto.event_id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )

        player_role = await player_role_repo.create(
            PlayerRoleCreate(event_player_id=event_player_dto.id, game_role_id=created.id, priority=1)
        )
        team_player = await team_player_repo.create(
            TeamPlayerCreate(team_id=team_dto.id, member_id=uuid.uuid4(), game_role_id=created.id, rating=4.0)
        )

        fetched = await selected_game_role_repo.get(created.id, load_player_roles=True, load_team_players=True)
        assert fetched is not None
        assert len(fetched.player_roles) == 1
        assert len(fetched.team_players) == 1
        assert fetched.player_roles[0].id == player_role.id
        assert fetched.team_players[0].id == team_player.id

    async def test_update_selected_game_role_override_count(self, selected_game_role_repo, event_dto):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=event_dto.id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )
        updated = await selected_game_role_repo.update(
            SelectedGameRoleUpdate(id=created.id, override_max_count=5)
        )
        assert updated.override_max_count == 5
        assert updated.override_min_count == 1

    async def test_list_selected_game_roles_by_event(self, selected_game_role_repo, event_dto):
        for i in range(3):
            await selected_game_role_repo.create(
                SelectedGameRoleCreate(
                    event_id=event_dto.id,
                    game_role_id=uuid.uuid4(),
                    override_max_count=i + 1,
                    override_min_count=1,
                )
            )

        listed = await selected_game_role_repo.list_by_event(event_dto.id)
        assert len(listed) == 3
        assert all(r.event_id == event_dto.id for r in listed)

    async def test_exists_selected_game_role(self, selected_game_role_repo, event_dto):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=event_dto.id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )
        assert await selected_game_role_repo.exists(created.id) is True

    async def test_exists_non_existent_selected_game_role_returns_false(self, selected_game_role_repo):
        assert await selected_game_role_repo.exists(uuid.uuid4()) is False

    async def test_delete_selected_game_role(
        self,
        selected_game_role_repo,
        player_role_repo,
        team_player_repo,
        event_player_dto,
        team_dto,
    ):
        created = await selected_game_role_repo.create(
            SelectedGameRoleCreate(
                event_id=team_dto.event_id,
                game_role_id=uuid.uuid4(),
                override_max_count=4,
                override_min_count=1,
            )
        )

        player_role = await player_role_repo.create(
            PlayerRoleCreate(event_player_id=event_player_dto.id, game_role_id=created.id, priority=1)
        )
        team_player = await team_player_repo.create(
            TeamPlayerCreate(team_id=team_dto.id, member_id=uuid.uuid4(), game_role_id=created.id, rating=4.0)
        )

        await player_role_repo.delete(player_role.id)
        await team_player_repo.delete(team_player.id)
        assert await selected_game_role_repo.delete(created.id) is True
        assert await selected_game_role_repo.get(created.id) is None

    async def test_delete_non_existent_selected_game_role_returns_false(self, selected_game_role_repo):
        assert await selected_game_role_repo.delete(uuid.uuid4()) is False



