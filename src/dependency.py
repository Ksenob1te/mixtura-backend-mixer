from typing import Annotated

from faststream import Context, ContextRepo, Depends
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from .core.interfaces.repo.balancer_request import BalancerRequestRepositoryProtocol
from .core.interfaces.repo.rating import RatingClientProtocol
from .core.interfaces.repo import (
    ApplicationCustomFieldRepositoryProtocol,
    ApplicationIntegrationRepositoryProtocol,
    ApplicationRepositoryProtocol,
    ApplicationTimeSettingsRepositoryProtocol,
    BalancerTaskStoreProtocol,
    BracketPlacementRepositoryProtocol,
    BracketRepositoryProtocol,
    DraftedPlayerRepositoryProtocol,
    DraftRepositoryProtocol,
    EventRepositoryProtocol,
    FilledApplicationFieldRepositoryProtocol,
    MatchRepositoryProtocol,
    MatchScoreRepositoryProtocol,
    MatchSlotRepositoryProtocol,
    OrganizerRepositoryProtocol,
    PlayerRepositoryProtocol,
    PlayerRoleRepositoryProtocol,
    RequiredIntegrationRepositoryProtocol,
    RoundRobinSettingsRepositoryProtocol,
    SelectedGameRoleRepositoryProtocol,
    StageGroupRepositoryProtocol,
    StageRepositoryProtocol,
    SwissSettingsRepositoryProtocol,
    TeamFormationVariantStoreProtocol,
    TeamPlayerRepositoryProtocol,
    TeamRepositoryProtocol,
)
from src.infra.clients.balancer_request import BalancerRequestRepository
from src.infra.clients.rating import RatingClient
from src.infra.postgre import DatabaseSessionManager
from src.infra.postgre.repo import (
    ApplicationCustomFieldRepository,
    ApplicationIntegrationRepository,
    ApplicationRepository,
    ApplicationTimeSettingsRepository,
    BracketPlacementRepository,
    BracketRepository,
    DraftRepository,
    DraftedPlayerRepository,
    EventRepository,
    FilledApplicationFieldRepository,
    MatchRepository,
    MatchScoreRepository,
    MatchSlotRepository,
    OrganizerRepository,
    PlayerRepository,
    PlayerRoleRepository,
    RequiredIntegrationRepository,
    RoundRobinSettingsRepository,
    SelectedGameRoleRepository,
    StageGroupRepository,
    StageRepository,
    SwissSettingsRepository,
    TeamPlayerRepository,
    TeamRepository,
)
from src.infra.rabbit.rpc_client import RabbitRpcClient
from src.infra.redis.balancer_task import BalancerTaskStore
from src.infra.redis.engine import RedisSessionManager
from src.infra.redis.team_formation import TeamFormationVariantStore
from src.core.services import (
    ApplicationService,
    DraftService,
    EventService,
    MatchService,
    OrganizerService,
    PlayerService,
    SettingsService,
    TeamService,
    TeamFormationService,
)
from src.env_config import env


async def get_db_session(
    session_manager: Annotated[DatabaseSessionManager, Context()],
    context: ContextRepo,
):
    async with session_manager.session() as session:
        token = context.set_local("db_session", session)
        try:
            yield session
        finally:
            context.reset_local("db_session", token)


DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_redis_session(
    redis_engine: Annotated[RedisSessionManager, Context()],
):
    async with redis_engine.client() as redis:
        yield redis


RedisSession = Annotated[Redis, Depends(get_redis_session)]

# --- Repository providers ---

async def get_event_repository(session: DatabaseSession) -> EventRepositoryProtocol:
    return EventRepository(session)


async def get_organizer_repository(session: DatabaseSession) -> OrganizerRepositoryProtocol:
    return OrganizerRepository(session)


async def get_application_repository(session: DatabaseSession) -> ApplicationRepositoryProtocol:
    return ApplicationRepository(session)


async def get_application_custom_field_repository(session: DatabaseSession) -> ApplicationCustomFieldRepositoryProtocol:
    return ApplicationCustomFieldRepository(session)


async def get_application_integration_repository(session: DatabaseSession) -> ApplicationIntegrationRepositoryProtocol:
    return ApplicationIntegrationRepository(session)


async def get_application_time_settings_repository(session: DatabaseSession) -> ApplicationTimeSettingsRepositoryProtocol:
    return ApplicationTimeSettingsRepository(session)


async def get_bracket_repository(session: DatabaseSession) -> BracketRepositoryProtocol:
    return BracketRepository(session)


async def get_bracket_placement_repository(session: DatabaseSession) -> BracketPlacementRepositoryProtocol:
    return BracketPlacementRepository(session)


async def get_draft_repository(session: DatabaseSession) -> DraftRepositoryProtocol:
    return DraftRepository(session)


async def get_drafted_player_repository(session: DatabaseSession) -> DraftedPlayerRepositoryProtocol:
    return DraftedPlayerRepository(session)


async def get_filled_application_field_repository(session: DatabaseSession) -> FilledApplicationFieldRepositoryProtocol:
    return FilledApplicationFieldRepository(session)


async def get_match_repository(session: DatabaseSession) -> MatchRepositoryProtocol:
    return MatchRepository(session)


async def get_match_score_repository(session: DatabaseSession) -> MatchScoreRepositoryProtocol:
    return MatchScoreRepository(session)


async def get_match_slot_repository(session: DatabaseSession) -> MatchSlotRepositoryProtocol:
    return MatchSlotRepository(session)


async def get_player_repository(session: DatabaseSession) -> PlayerRepositoryProtocol:
    return PlayerRepository(session)


async def get_player_role_repository(session: DatabaseSession) -> PlayerRoleRepositoryProtocol:
    return PlayerRoleRepository(session)


async def get_required_integration_repository(session: DatabaseSession) -> RequiredIntegrationRepositoryProtocol:
    return RequiredIntegrationRepository(session)


async def get_round_robin_settings_repository(session: DatabaseSession) -> RoundRobinSettingsRepositoryProtocol:
    return RoundRobinSettingsRepository(session)


async def get_selected_game_role_repository(session: DatabaseSession) -> SelectedGameRoleRepositoryProtocol:
    return SelectedGameRoleRepository(session)


async def get_stage_repository(session: DatabaseSession) -> StageRepositoryProtocol:
    return StageRepository(session)


async def get_stage_group_repository(session: DatabaseSession) -> StageGroupRepositoryProtocol:
    return StageGroupRepository(session)


async def get_swiss_settings_repository(session: DatabaseSession) -> SwissSettingsRepositoryProtocol:
    return SwissSettingsRepository(session)


async def get_team_repository(session: DatabaseSession) -> TeamRepositoryProtocol:
    return TeamRepository(session)


async def get_team_player_repository(session: DatabaseSession) -> TeamPlayerRepositoryProtocol:
    return TeamPlayerRepository(session)


# -- Client providers --

async def get_rpc_client(
    rpc_client: Annotated[RabbitRpcClient, Context()],
) -> RabbitRpcClient:
    return rpc_client


async def get_rating_client(
    rpc_client: Annotated[RabbitRpcClient, Context()],
    broker: Annotated[RabbitBroker, Context()],
) -> RatingClientProtocol:
    return RatingClient(rpc_client, broker)


async def get_balancer_request_repository(
    broker: Annotated[RabbitBroker, Context()],
) -> BalancerRequestRepositoryProtocol:
    return BalancerRequestRepository(broker)


# -- Store providers --

async def get_team_formation_variant_store(
    redis: RedisSession,
) -> TeamFormationVariantStoreProtocol:
    return TeamFormationVariantStore(redis)


async def get_balancer_task_store(
    redis: RedisSession,
) -> BalancerTaskStoreProtocol:
    return BalancerTaskStore(redis)


# -- Repository type aliases --

EventRepositoryDependency = Annotated[EventRepository, Depends(get_event_repository)]
OrganizerRepositoryDependency = Annotated[
    OrganizerRepository, Depends(get_organizer_repository)
]
ApplicationRepositoryDependency = Annotated[
    ApplicationRepository, Depends(get_application_repository)
]
ApplicationCustomFieldRepositoryDependency = Annotated[
    ApplicationCustomFieldRepository, Depends(get_application_custom_field_repository)
]
ApplicationIntegrationRepositoryDependency = Annotated[
    ApplicationIntegrationRepository, Depends(get_application_integration_repository)
]
ApplicationTimeSettingsRepositoryDependency = Annotated[
    ApplicationTimeSettingsRepository,
    Depends(get_application_time_settings_repository),
]
BracketRepositoryDependency = Annotated[
    BracketRepository, Depends(get_bracket_repository)
]
BracketPlacementRepositoryDependency = Annotated[
    BracketPlacementRepository, Depends(get_bracket_placement_repository)
]
DraftRepositoryDependency = Annotated[
    DraftRepository, Depends(get_draft_repository)
]
DraftedPlayerRepositoryDependency = Annotated[
    DraftedPlayerRepository, Depends(get_drafted_player_repository)
]
FilledApplicationFieldRepositoryDependency = Annotated[
    FilledApplicationFieldRepository, Depends(get_filled_application_field_repository)
]
MatchRepositoryDependency = Annotated[
    MatchRepository, Depends(get_match_repository)
]
MatchScoreRepositoryDependency = Annotated[
    MatchScoreRepository, Depends(get_match_score_repository)
]
MatchSlotRepositoryDependency = Annotated[
    MatchSlotRepository, Depends(get_match_slot_repository)
]
PlayerRepositoryDependency = Annotated[
    PlayerRepository, Depends(get_player_repository)
]
PlayerRoleRepositoryDependency = Annotated[
    PlayerRoleRepository, Depends(get_player_role_repository)
]
RequiredIntegrationRepositoryDependency = Annotated[
    RequiredIntegrationRepository, Depends(get_required_integration_repository)
]
RoundRobinSettingsRepositoryDependency = Annotated[
    RoundRobinSettingsRepository, Depends(get_round_robin_settings_repository)
]
SelectedGameRoleRepositoryDependency = Annotated[
    SelectedGameRoleRepository, Depends(get_selected_game_role_repository)
]
StageRepositoryDependency = Annotated[
    StageRepository, Depends(get_stage_repository)
]
StageGroupRepositoryDependency = Annotated[
    StageGroupRepository, Depends(get_stage_group_repository)
]
SwissSettingsRepositoryDependency = Annotated[
    SwissSettingsRepository, Depends(get_swiss_settings_repository)
]
TeamRepositoryDependency = Annotated[
    TeamRepository, Depends(get_team_repository)
]
TeamPlayerRepositoryDependency = Annotated[
    TeamPlayerRepository, Depends(get_team_player_repository)
]

# -- Client type aliases --

RatingClientDependency = Annotated[RatingClientProtocol, Depends(get_rating_client)]
BalancerRequestRepositoryDependency = Annotated[BalancerRequestRepositoryProtocol, Depends(get_balancer_request_repository)]

# -- Store type aliases --

TeamFormationVariantStoreDependency = Annotated[TeamFormationVariantStoreProtocol, Depends(get_team_formation_variant_store)]
BalancerTaskStoreDependency = Annotated[BalancerTaskStoreProtocol, Depends(get_balancer_task_store)]

# -- Service providers --

async def get_event_service(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    time_settings_repo: ApplicationTimeSettingsRepositoryDependency,
    match_repo: MatchRepositoryDependency,
) -> EventService:
    return EventService(event_repo, organizer_repo, time_settings_repo, match_repo)


async def get_organizer_service(
    organizer_repo: OrganizerRepositoryDependency,
    event_repo: EventRepositoryDependency,
) -> OrganizerService:
    return OrganizerService(organizer_repo, event_repo)


async def get_player_service(
    event_repo: EventRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    player_role_repo: PlayerRoleRepositoryDependency,
) -> PlayerService:
    return PlayerService(event_repo, player_repo, player_role_repo)


async def get_application_service(
    event_repo: EventRepositoryDependency,
    application_repo: ApplicationRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    player_role_repo: PlayerRoleRepositoryDependency,
    filled_field_repo: FilledApplicationFieldRepositoryDependency,
    application_integration_repo: ApplicationIntegrationRepositoryDependency,
) -> ApplicationService:
    return ApplicationService(
        event_repo, application_repo, player_repo, player_role_repo,
        filled_field_repo, application_integration_repo,
    )


async def get_draft_service(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    drafted_player_repo: DraftedPlayerRepositoryDependency,
    match_repo: MatchRepositoryDependency,
) -> DraftService:
    return DraftService(event_repo, organizer_repo, player_repo, draft_repo, drafted_player_repo, match_repo)


async def get_team_service(
    team_repo: TeamRepositoryDependency,
    event_repo: EventRepositoryDependency,
) -> TeamService:
    return TeamService(team_repo, event_repo)


async def get_team_formation_service(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    team_player_repo: TeamPlayerRepositoryDependency,
    variant_store: TeamFormationVariantStoreDependency,
    rating_client: RatingClientDependency,
    balancer_repo: BalancerRequestRepositoryDependency,
    balancer_task_store: BalancerTaskStoreDependency,
) -> TeamFormationService:
    return TeamFormationService(
        event_repo, organizer_repo, draft_repo, player_repo,
        team_repo, team_player_repo, variant_store, rating_client,
        balancer_repo, balancer_task_store, env,
    )


async def get_match_service(
    event_repo: EventRepositoryDependency,
    bracket_repo: BracketRepositoryDependency,
    stage_repo: StageRepositoryDependency,
    stage_group_repo: StageGroupRepositoryDependency,
    match_repo: MatchRepositoryDependency,
    match_slot_repo: MatchSlotRepositoryDependency,
    match_score_repo: MatchScoreRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
) -> MatchService:
    return MatchService(
        event_repo, bracket_repo, stage_repo, stage_group_repo,
        match_repo, match_slot_repo, match_score_repo, team_repo,
        draft_repo, player_repo,
    )


async def get_settings_service(
    event_repo: EventRepositoryDependency,
    integration_repo: RequiredIntegrationRepositoryDependency,
    role_repo: SelectedGameRoleRepositoryDependency,
    field_repo: ApplicationCustomFieldRepositoryDependency,
    time_repo: ApplicationTimeSettingsRepositoryDependency,
) -> SettingsService:
    return SettingsService(event_repo, integration_repo, role_repo, field_repo, time_repo)


# -- Service type aliases --

EventServiceDependency = Annotated[EventService, Depends(get_event_service)]
OrganizerServiceDependency = Annotated[OrganizerService, Depends(get_organizer_service)]
PlayerServiceDependency = Annotated[PlayerService, Depends(get_player_service)]
ApplicationServiceDependency = Annotated[ApplicationService, Depends(get_application_service)]
DraftServiceDependency = Annotated[DraftService, Depends(get_draft_service)]
TeamServiceDependency = Annotated[TeamService, Depends(get_team_service)]
TeamFormationServiceDependency = Annotated[TeamFormationService, Depends(get_team_formation_service)]
MatchServiceDependency = Annotated[MatchService, Depends(get_match_service)]
SettingsServiceDependency = Annotated[SettingsService, Depends(get_settings_service)]
