import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.application import ApplicationService
from src.core.services.draft import DraftService
from src.core.services.event import EventService
from src.core.services.match import MatchService
from src.core.services.organizer import OrganizerService
from src.core.services.player import PlayerService
from src.core.services.settings import SettingsService
from src.core.services.team import TeamService
from src.core.services.team_formation import TeamFormationService
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
from src.infra.postgre.repo.organizer import OrganizerRepository
from src.infra.postgre.repo.player import PlayerRepository
from src.infra.postgre.repo.player_role import PlayerRoleRepository
from src.infra.postgre.repo.required_integration import RequiredIntegrationRepository
from src.infra.postgre.repo.selected_game_role import SelectedGameRoleRepository
from src.infra.postgre.repo.stage import StageRepository
from src.infra.postgre.repo.stage_group import StageGroupRepository
from src.infra.postgre.repo.team import TeamRepository
from src.infra.postgre.repo.team_player import TeamPlayerRepository


@pytest.fixture
def server_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def member_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def organizer_id() -> uuid.UUID:
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
def organizer_repo(async_session: AsyncSession) -> OrganizerRepository:
    return OrganizerRepository(async_session)


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
def event_service(
    event_repo,
    organizer_repo,
    application_time_settings_repo,
    match_repo,
) -> EventService:
    return EventService(
        event_repo=event_repo,
        organizer_repo=organizer_repo,
        time_settings_repo=application_time_settings_repo,
        match_repo=match_repo,
    )


@pytest.fixture
def application_service(
    event_repo,
    application_repo,
    player_repo,
    player_role_repo,
    filled_application_field_repo,
    application_integration_repo,
) -> ApplicationService:
    return ApplicationService(
        event_repo=event_repo,
        application_repo=application_repo,
        player_repo=player_repo,
        player_role_repo=player_role_repo,
        filled_field_repo=filled_application_field_repo,
        application_integration_repo=application_integration_repo,
    )


@pytest.fixture
def draft_service(
    event_repo,
    organizer_repo,
    player_repo,
    draft_repo,
    drafted_player_repo,
    match_repo,
) -> DraftService:
    return DraftService(
        event_repo=event_repo,
        organizer_repo=organizer_repo,
        player_repo=player_repo,
        draft_repo=draft_repo,
        drafted_player_repo=drafted_player_repo,
        match_repo=match_repo,
    )


@pytest.fixture
def organizer_service(organizer_repo, event_repo) -> OrganizerService:
    return OrganizerService(organizer_repo=organizer_repo, event_repo=event_repo)


@pytest.fixture
def player_service(event_repo, player_repo) -> PlayerService:
    return PlayerService(event_repo=event_repo, player_repo=player_repo)


@pytest.fixture
def settings_service(
    event_repo,
    required_integration_repo,
    selected_game_role_repo,
    application_custom_field_repo,
    application_time_settings_repo,
) -> SettingsService:
    return SettingsService(
        event_repo=event_repo,
        integration_repo=required_integration_repo,
        role_repo=selected_game_role_repo,
        field_repo=application_custom_field_repo,
        time_repo=application_time_settings_repo,
    )


@pytest.fixture
def team_service(team_repo, event_repo) -> TeamService:
    return TeamService(team_repo=team_repo, event_repo=event_repo)


@pytest.fixture
def match_service(
    event_repo,
    bracket_repo,
    stage_repo,
    stage_group_repo,
    match_repo,
    match_slot_repo,
    match_score_repo,
    team_repo,
    draft_repo,
    player_repo,
    rating_client,
    match_env,
) -> MatchService:
    return MatchService(
        event_repo=event_repo,
        bracket_repo=bracket_repo,
        stage_repo=stage_repo,
        stage_group_repo=stage_group_repo,
        match_repo=match_repo,
        match_slot_repo=match_slot_repo,
        match_score_repo=match_score_repo,
        team_repo=team_repo,
        draft_repo=draft_repo,
        player_repo=player_repo,
        rating_client=rating_client,
        env=match_env,
    )


@pytest.fixture
def team_formation_service(
    event_repo,
    organizer_repo,
    draft_repo,
    player_repo,
    team_repo,
    team_player_repo,
    variant_store,
    rating_client,
    balancer_repo,
    balancer_task_store,
    team_formation_env,
) -> TeamFormationService:
    return TeamFormationService(
        event_repo=event_repo,
        organizer_repo=organizer_repo,
        draft_repo=draft_repo,
        player_repo=player_repo,
        team_repo=team_repo,
        team_player_repo=team_player_repo,
        variant_store=variant_store,
        rating_client=rating_client,
        balancer_repo=balancer_repo,
        balancer_task_store=balancer_task_store,
        env=team_formation_env,
    )


class RecordingVariantStore:
    def __init__(self):
        self.saved_jobs: dict[tuple[uuid.UUID, uuid.UUID], dict] = {}
        self.deleted: list[tuple[uuid.UUID, uuid.UUID, uuid.UUID]] = []

    async def save(self, job_id, event_id, draft_id, job, ttl):
        self.saved_jobs[(event_id, draft_id)] = {"job_id": job_id, "job": job, "ttl": ttl}

    async def get_latest_by_draft(self, event_id, draft_id):
        entry = self.saved_jobs.get((event_id, draft_id))
        return None if entry is None else entry["job"]

    async def delete(self, job_id, event_id, draft_id):
        self.deleted.append((job_id, event_id, draft_id))
        self.saved_jobs.pop((event_id, draft_id), None)


class RecordingBalancerRepo:
    def __init__(self, variants=None):
        self.variants = variants or []
        self.mix_calls: list[dict] = []
        self.tournament_calls: list[dict] = []

    async def request_mix_formation(self, *, task_id, draft_id, players, settings):
        self.mix_calls.append({"task_id": task_id, "draft_id": draft_id, "players": players, "settings": settings})

    async def request_tournament_formation(self, *, task_id, draft_id, players, settings):
        self.tournament_calls.append({"task_id": task_id, "draft_id": draft_id, "players": players, "settings": settings})


class RecordingBalancerTaskStore:
    def __init__(self):
        self.tasks: dict = {}

    async def save(self, task, ttl):
        self.tasks[task.task_id] = task

    async def get(self, task_id):
        return self.tasks.get(task_id, None)

    async def delete(self, task_id):
        self.tasks.pop(task_id, None)


class RecordingRatingClient:
    def __init__(self):
        self.calls = []

    async def process_match_result(self, **kwargs):
        self.calls.append(kwargs)

    async def calculate_effective_ratings(self, **kwargs):
        self.calls.append(kwargs)
        return []


class MatchEnvStub:
    rating_match_process_enabled = False


class TeamFormationEnvStub:
    team_formation_variants_ttl_seconds = 3600


@pytest.fixture
def variant_store() -> RecordingVariantStore:
    return RecordingVariantStore()


@pytest.fixture
def balancer_repo() -> RecordingBalancerRepo:
    return RecordingBalancerRepo()


@pytest.fixture
def balancer_task_store() -> RecordingBalancerTaskStore:
    return RecordingBalancerTaskStore()


@pytest.fixture
def rating_client() -> RecordingRatingClient:
    return RecordingRatingClient()


@pytest.fixture
def match_env() -> MatchEnvStub:
    return MatchEnvStub()


@pytest.fixture
def team_formation_env() -> TeamFormationEnvStub:
    return TeamFormationEnvStub()
