import uuid
import pytest

from src.core.models.team_player import TeamPlayerCreate


pytestmark = pytest.mark.asyncio


class TestTeamPlayerRepository:
    async def test_create_team_player(self, team_player_repo, team_dto, selected_game_role_dto):
        created = await team_player_repo.create(
            TeamPlayerCreate(
                team_id=team_dto.id,
                member_id=uuid.uuid4(),
                game_role_id=selected_game_role_dto.id,
                rating=4.5,
            )
        )
        assert created.id is not None
        assert created.team_id == team_dto.id
        assert created.game_role_id == selected_game_role_dto.id
        assert created.rating == 4.5

    async def test_get_team_player_by_id(self, team_player_repo, team_dto, selected_game_role_dto):
        created = await team_player_repo.create(
            TeamPlayerCreate(
                team_id=team_dto.id,
                member_id=uuid.uuid4(),
                game_role_id=selected_game_role_dto.id,
                rating=3.5,
            )
        )
        fetched = await team_player_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.rating == 3.5

    async def test_get_non_existent_team_player_returns_none(self, team_player_repo):
        fetched = await team_player_repo.get(uuid.uuid4())
        assert fetched is None

    async def test_get_team_player_with_relations(self, team_player_repo, team_dto, selected_game_role_dto):
        member_id = uuid.uuid4()
        created = await team_player_repo.create(
            TeamPlayerCreate(
                team_id=team_dto.id,
                member_id=member_id,
                game_role_id=selected_game_role_dto.id,
                rating=4.0,
            )
        )
        fetched = await team_player_repo.get(created.id, load_team=True, load_role=True)
        assert fetched is not None
        assert fetched.team is not None
        assert fetched.team.id == team_dto.id
        assert fetched.game_role is not None
        assert fetched.game_role.id == selected_game_role_dto.id

    async def test_list_team_players_by_team(self, team_player_repo, team_dto, selected_game_role_dto):
        for i in range(3):
            await team_player_repo.create(
                TeamPlayerCreate(
                    team_id=team_dto.id,
                    member_id=uuid.uuid4(),
                    game_role_id=selected_game_role_dto.id,
                    rating=i + 1.0,
                )
            )
        listed = await team_player_repo.list_by_team(team_dto.id)
        assert len(listed) == 3
        assert all(p.team_id == team_dto.id for p in listed)

    async def test_list_team_players_filtered_by_game_role(self, team_player_repo, team_dto, selected_game_role_dto, selected_game_role_repo):
        # create another selected game role for the same event
        other_role = await selected_game_role_repo.create(
            __import__('src.core.models.selected_game_role', fromlist=['SelectedGameRoleCreate']).SelectedGameRoleCreate(
                event_id=team_dto.event_id, game_role_id=__import__('uuid', fromlist=['uuid4']).uuid4(), override_max_count=2, override_min_count=1
            )
        )

        # create players with same team but alternating game roles
        for i in range(4):
            gid = selected_game_role_dto.id if i % 2 == 0 else other_role.id
            await team_player_repo.create(
                TeamPlayerCreate(
                    team_id=team_dto.id,
                    member_id=uuid.uuid4(),
                    game_role_id=gid,
                    rating=1.0 + i,
                )
            )

        listed = await team_player_repo.list_by_team(team_dto.id)
        # filter locally by game_role_id since repo doesn't support list_by_game_role
        filtered = [p for p in listed if p.game_role_id == selected_game_role_dto.id]
        assert len(filtered) >= 1

    async def test_exists_team_player(self, team_player_repo, team_dto, selected_game_role_dto):
        created = await team_player_repo.create(
            TeamPlayerCreate(
                team_id=team_dto.id,
                member_id=uuid.uuid4(),
                game_role_id=selected_game_role_dto.id,
                rating=4.0,
            )
        )
        assert await team_player_repo.exists(created.id) is True

    async def test_exists_non_existent_team_player_returns_false(self, team_player_repo):
        assert await team_player_repo.exists(uuid.uuid4()) is False

    async def test_delete_team_player(self, team_player_repo, team_dto, selected_game_role_dto):
        created = await team_player_repo.create(
            TeamPlayerCreate(
                team_id=team_dto.id,
                member_id=uuid.uuid4(),
                game_role_id=selected_game_role_dto.id,
                rating=4.0,
            )
        )
        assert await team_player_repo.delete(created.id) is True
        fetched = await team_player_repo.get(created.id)
        assert fetched is None

    async def test_delete_non_existent_team_player_returns_false(self, team_player_repo):
        assert await team_player_repo.delete(uuid.uuid4()) is False




