import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models.application import ApplicationCreate, ApplicationStatus
from src.core.models.application_custom_field import ApplicationCustomFieldCreate, ApplicationCustomFieldUpdate
from src.core.models.application_integration import ApplicationIntegrationCreate
from src.core.models.application_time_settings import ApplicationTimeSettingsCreate, ApplicationTimeSettingsUpdate
from src.core.models.bracket import BracketCreate
from src.core.models.bracket_placement import BracketPlacementCreate
from src.core.models.draft import DraftCreate
from src.core.models.drafted_player import DraftedPlayerCreate
from src.core.models.event import Event, EventCreate, EventMatchType, TeamFormation
from src.core.models.event_player import EventPlayerCreate
from src.core.models.filled_application_field import FilledApplicationFieldCreate
from src.core.models.match import MatchCreate
from src.core.models.match_score import MatchScoreCreate, MatchScoreUpdate
from src.core.models.match_slot import MatchSlotCreate, MatchSlotSourceType
from src.core.models.player_role import PlayerRoleCreate
from src.core.models.required_integration import RequiredIntegrationCreate
from src.core.models.round_robin_settings import RoundRobinSettingsCreate
from src.core.models.selected_game_role import SelectedGameRoleCreate, SelectedGameRoleUpdate
from src.core.models.stage import StageCreate, StageFormat
from src.core.models.stage_group import StageGroupCreate
from src.core.models.swiss_settings import SwissSettingsCreate
from src.core.models.team import TeamCreate
from src.core.models.team_player import TeamPlayerCreate
from src.infra.postgre.repo.application import ApplicationRepository
from src.infra.postgre.repo.application_custom_field import ApplicationCustomFieldRepository
from src.infra.postgre.repo.application_integration import ApplicationIntegrationRepository
from src.infra.postgre.repo.application_time_settings import ApplicationTimeSettingsRepository
from src.infra.postgre.repo.bracket import BracketRepository
from src.infra.postgre.repo.bracket_placement import BracketPlacementRepository
from src.infra.postgre.repo.draft import DraftRepository
from src.infra.postgre.repo.drafted_player import DraftedPlayerRepository
from src.infra.postgre.repo.event import EventRepository
from src.infra.postgre.repo.filled_application_field import FilledApplicationFieldRepository
from src.infra.postgre.repo.match import MatchRepository
from src.infra.postgre.repo.match_score import MatchScoreRepository
from src.infra.postgre.repo.match_slot import MatchSlotRepository
from src.infra.postgre.repo.player import PlayerRepository
from src.infra.postgre.repo.player_role import PlayerRoleRepository
from src.infra.postgre.repo.required_integration import RequiredIntegrationRepository
from src.infra.postgre.repo.round_robin_settings import RoundRobinSettingsRepository
from src.infra.postgre.repo.selected_game_role import SelectedGameRoleRepository
from src.infra.postgre.repo.stage import StageRepository
from src.infra.postgre.repo.stage_group import StageGroupRepository
from src.infra.postgre.repo.swiss_settings import SwissSettingsRepository
from src.infra.postgre.repo.team import TeamRepository
from src.infra.postgre.repo.team_player import TeamPlayerRepository


@pytest.fixture
def server_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def event_repo(async_session: AsyncSession) -> EventRepository:
    return EventRepository(async_session)


@pytest.fixture
def bracket_repo(async_session: AsyncSession) -> BracketRepository:
    return BracketRepository(async_session)


@pytest.fixture
def stage_repo(async_session: AsyncSession) -> StageRepository:
    return StageRepository(async_session)


@pytest.fixture
def stage_group_repo(async_session: AsyncSession) -> StageGroupRepository:
    return StageGroupRepository(async_session)


@pytest.fixture
def team_repo(async_session: AsyncSession) -> TeamRepository:
    return TeamRepository(async_session)


@pytest.fixture
def draft_repo(async_session: AsyncSession) -> DraftRepository:
    return DraftRepository(async_session)


@pytest.fixture
def application_repo(async_session: AsyncSession) -> ApplicationRepository:
    return ApplicationRepository(async_session)


@pytest.fixture
def player_repo(async_session: AsyncSession) -> PlayerRepository:
    return PlayerRepository(async_session)


@pytest.fixture
def match_repo(async_session: AsyncSession) -> MatchRepository:
    return MatchRepository(async_session)


@pytest.fixture
def application_custom_field_repo(async_session: AsyncSession) -> ApplicationCustomFieldRepository:
    return ApplicationCustomFieldRepository(async_session)


@pytest.fixture
def application_integration_repo(async_session: AsyncSession) -> ApplicationIntegrationRepository:
    return ApplicationIntegrationRepository(async_session)


@pytest.fixture
def application_time_settings_repo(async_session: AsyncSession) -> ApplicationTimeSettingsRepository:
    return ApplicationTimeSettingsRepository(async_session)


@pytest.fixture
def filled_application_field_repo(async_session: AsyncSession) -> FilledApplicationFieldRepository:
    return FilledApplicationFieldRepository(async_session)


@pytest.fixture
def bracket_placement_repo(async_session: AsyncSession) -> BracketPlacementRepository:
    return BracketPlacementRepository(async_session)


@pytest.fixture
def drafted_player_repo(async_session: AsyncSession) -> DraftedPlayerRepository:
    return DraftedPlayerRepository(async_session)


@pytest.fixture
def required_integration_repo(async_session: AsyncSession) -> RequiredIntegrationRepository:
    return RequiredIntegrationRepository(async_session)


@pytest.fixture
def round_robin_settings_repo(async_session: AsyncSession) -> RoundRobinSettingsRepository:
    return RoundRobinSettingsRepository(async_session)


@pytest.fixture
def swiss_settings_repo(async_session: AsyncSession) -> SwissSettingsRepository:
    return SwissSettingsRepository(async_session)


@pytest.fixture
def selected_game_role_repo(async_session: AsyncSession) -> SelectedGameRoleRepository:
    return SelectedGameRoleRepository(async_session)


@pytest.fixture
def player_role_repo(async_session: AsyncSession) -> PlayerRoleRepository:
    return PlayerRoleRepository(async_session)


@pytest.fixture
def team_player_repo(async_session: AsyncSession) -> TeamPlayerRepository:
    return TeamPlayerRepository(async_session)


@pytest.fixture
def match_slot_repo(async_session: AsyncSession) -> MatchSlotRepository:
    return MatchSlotRepository(async_session)


@pytest.fixture
def match_score_repo(async_session: AsyncSession) -> MatchScoreRepository:
    return MatchScoreRepository(async_session)


@pytest.fixture
async def event_dto(event_repo: EventRepository, server_id: uuid.UUID) -> Event:
    return await event_repo.create(
        EventCreate(
            name="Additional Repo Event",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
            server_id=server_id,
        )
    )


@pytest.fixture
async def bracket_dto(bracket_repo: BracketRepository, event_dto: Event):
    return await bracket_repo.create(BracketCreate(event_id=event_dto.id))


@pytest.fixture
async def round_robin_stage_dto(stage_repo: StageRepository, bracket_dto):
    return await stage_repo.create(
        StageCreate(
            stage_index=1,
            bracket_id=bracket_dto.id,
            format=StageFormat.ROUND_ROBIN,
            name="Round Robin Stage",
        )
    )


@pytest.fixture
async def swiss_stage_dto(stage_repo: StageRepository, bracket_dto):
    return await stage_repo.create(
        StageCreate(
            stage_index=2,
            bracket_id=bracket_dto.id,
            format=StageFormat.SWISS,
            name="Swiss Stage",
        )
    )


@pytest.fixture
async def stage_group_dto(stage_group_repo: StageGroupRepository, round_robin_stage_dto):
    return await stage_group_repo.create(StageGroupCreate(stage_id=round_robin_stage_dto.id, name="Group A"))


@pytest.fixture
async def team_dto(team_repo: TeamRepository, event_dto: Event):
    return await team_repo.create(TeamCreate(event_id=event_dto.id, name="Team Alpha"))


@pytest.fixture
async def draft_dto(draft_repo: DraftRepository, event_dto: Event):
    return await draft_repo.create(DraftCreate(event_id=event_dto.id))


@pytest.fixture
async def application_dto(application_repo: ApplicationRepository, event_dto: Event):
    return await application_repo.create(
        ApplicationCreate(event_id=event_dto.id, member_id=uuid.uuid4(), status=ApplicationStatus.PENDING)
    )


@pytest.fixture
async def custom_field_dto(application_custom_field_repo: ApplicationCustomFieldRepository, event_dto: Event):
    return await application_custom_field_repo.create(
        ApplicationCustomFieldCreate(event_id=event_dto.id, name="Discord", is_private=True, is_required=False)
    )


@pytest.fixture
async def integration_dto(application_integration_repo: ApplicationIntegrationRepository, application_dto):
    return await application_integration_repo.create(
        ApplicationIntegrationCreate(
            application_id=application_dto.id,
            user_provider_id=uuid.uuid4(),
            provider_id=uuid.uuid4(),
            provider_name="discord",
        )
    )


@pytest.fixture
async def filled_field_dto(
    filled_application_field_repo: FilledApplicationFieldRepository,
    application_dto,
    custom_field_dto,
):
    return await filled_application_field_repo.create(
        FilledApplicationFieldCreate(
            value="tester#1234",
            custom_field_id=custom_field_dto.id,
            application_id=application_dto.id,
        )
    )


@pytest.fixture
async def event_player_dto(player_repo: PlayerRepository, event_dto: Event):
    return await player_repo.create(
        EventPlayerCreate(
            event_id=event_dto.id,
            member_id=uuid.uuid4(),
            is_draft_pinned=False,
        )
    )


@pytest.fixture
async def selected_game_role_dto(selected_game_role_repo: SelectedGameRoleRepository, event_dto: Event):
    return await selected_game_role_repo.create(
        SelectedGameRoleCreate(
            event_id=event_dto.id,
            game_role_id=uuid.uuid4(),
            override_max_count=3,
            override_min_count=1,
        )
    )


@pytest.fixture
async def player_role_dto(player_role_repo: PlayerRoleRepository, event_player_dto, selected_game_role_dto):
    return await player_role_repo.create(
        PlayerRoleCreate(
            event_player_id=event_player_dto.id,
            game_role_id=selected_game_role_dto.id,
            priority=1,
        )
    )


@pytest.fixture
async def team_player_dto(team_player_repo: TeamPlayerRepository, team_dto, selected_game_role_dto):
    return await team_player_repo.create(
        TeamPlayerCreate(
            team_id=team_dto.id,
            member_id=uuid.uuid4(),
            game_role_id=selected_game_role_dto.id,
            rating=4.5,
        )
    )


@pytest.fixture
async def bracket_placement_dto(bracket_placement_repo: BracketPlacementRepository, bracket_dto, team_dto):
    return await bracket_placement_repo.create(
        BracketPlacementCreate(bracket_id=bracket_dto.id, team_id=team_dto.id, placement=1)
    )


@pytest.fixture
async def required_integration_dto(required_integration_repo: RequiredIntegrationRepository, event_dto: Event):
    return await required_integration_repo.create(
        RequiredIntegrationCreate(event_id=event_dto.id, name="discord")
    )


@pytest.fixture
async def round_robin_settings_dto(round_robin_settings_repo: RoundRobinSettingsRepository, round_robin_stage_dto):
    return await round_robin_settings_repo.create(
        RoundRobinSettingsCreate(
            stage_id=round_robin_stage_dto.id,
            meetings_per_pair=2,
            score_system="points",
            score_per_win=3,
            score_per_draw=1,
        )
    )


@pytest.fixture
async def swiss_settings_dto(swiss_settings_repo: SwissSettingsRepository, swiss_stage_dto):
    return await swiss_settings_repo.create(
        SwissSettingsCreate(
            stage_id=swiss_stage_dto.id,
            score_per_win=3,
            score_per_draw=1,
            score_per_bye=3,
        )
    )


@pytest.fixture
async def match_dto(match_repo: MatchRepository, stage_group_dto):
    return await match_repo.create(MatchCreate(group_id=stage_group_dto.id, match_index=1))

