"""Test suite for TeamRepository."""
import uuid

import pytest

from src.core.models.draft import DraftCreate
from src.core.models.event import EventCreate, EventMatchType, TeamFormation
from src.core.models.team import Team, TeamCreate, TeamUpdate
from src.infra.postgre.exceptions import IntegrityForeignException

pytestmark = pytest.mark.asyncio


class TestTeamRepository:
    async def test_create_team(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="Alpha"))

        assert isinstance(created, Team)
        assert created.event_id == event_dto.id
        assert created.draft_id is None
        assert created.name == "Alpha"

    async def test_create_team_without_draft_optional(self, team_repo, event_dto):
        created = await team_repo.create(
            TeamCreate(event_id=event_dto.id, draft_id=None, name="Standalone")
        )

        assert created.draft_id is None

    async def test_create_team_with_draft(self, team_repo, draft_repo, event_dto):
        draft = await draft_repo.create(DraftCreate(event_id=event_dto.id))
        created = await team_repo.create(
            TeamCreate(event_id=event_dto.id, draft_id=draft.id, name="Draft Team")
        )

        assert created.draft_id == draft.id

    async def test_create_team_foreign_key_violation(self, team_repo):
        with pytest.raises(IntegrityForeignException):
            await team_repo.create(TeamCreate(event_id=uuid.uuid4(), name="Invalid Team"))

    async def test_get_team_by_id(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="Lookup"))
        retrieved = await team_repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Lookup"

    async def test_get_team_with_event_relation(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="With Event"))
        retrieved = await team_repo.get(created.id, load_event=True)

        assert retrieved is not None
        assert retrieved.event is not None
        assert retrieved.event.id == event_dto.id

    async def test_get_team_with_players_relation(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="With Players"))
        retrieved = await team_repo.get(created.id, load_players=True)

        assert retrieved is not None
        assert retrieved.players == []

    async def test_list_by_event(self, team_repo, event_dto):
        for i in range(3):
            await team_repo.create(TeamCreate(event_id=event_dto.id, name=f"Team {i + 1}"))

        teams = await team_repo.list_by_event(event_dto.id)

        assert len(teams) == 3
        assert all(team.event_id == event_dto.id for team in teams)

    async def test_list_by_event_with_pagination(self, team_repo, event_dto):
        for i in range(5):
            await team_repo.create(TeamCreate(event_id=event_dto.id, name=f"Team {i + 1}"))

        assert len(await team_repo.list_by_event(event_dto.id, offset=0, limit=2)) == 2
        assert len(await team_repo.list_by_event(event_dto.id, offset=2, limit=2)) == 2
        assert len(await team_repo.list_by_event(event_dto.id, offset=4, limit=2)) == 1

    async def test_list_by_event_empty_when_no_teams(self, team_repo, event_dto):
        assert await team_repo.list_by_event(event_dto.id) == []

    async def test_update_team(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="Original"))
        updated = await team_repo.update(TeamUpdate(id=created.id, name="Updated"))

        assert updated.name == "Updated"
        assert updated.event_id == event_dto.id
        assert updated.id == created.id

    async def test_delete_team(self, team_repo, event_dto):
        created = await team_repo.create(TeamCreate(event_id=event_dto.id, name="Delete Me"))

        assert await team_repo.delete(created.id) is True
        assert await team_repo.get(created.id) is None

    async def test_delete_non_existent_team_returns_false(self, team_repo):
        assert await team_repo.delete(uuid.uuid4()) is False

    async def test_list_teams_different_events_isolated(self, team_repo, event_repo, draft_repo, server_id):
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

        draft1 = await draft_repo.create(DraftCreate(event_id=event1.id))
        draft2 = await draft_repo.create(DraftCreate(event_id=event2.id))

        await team_repo.create(TeamCreate(event_id=event1.id, draft_id=draft1.id, name="Event1 Team"))
        await team_repo.create(TeamCreate(event_id=event2.id, draft_id=draft2.id, name="Event2 Team"))

        assert len(await team_repo.list_by_event(event1.id)) == 1
        assert len(await team_repo.list_by_event(event2.id)) == 1
