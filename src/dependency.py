from typing import Annotated

from faststream import Context, ContextRepo, Depends
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from .core.interfaces.repo import (
    ApplicationCustomFieldRepositoryProtocol,
    ApplicationIntegrationRepositoryProtocol,
    ApplicationRepositoryProtocol,
    ApplicationTimeSettingsRepositoryProtocol,
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
    TeamPlayerRepositoryProtocol,
    TeamRepositoryProtocol,
)
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
from src.infra.redis.engine import RedisSessionManager
from src.infra.redis.team_formation import TeamFormationVariantStore
from src.infra.clients.rating import RatingClient
from src.infra.clients.mix_balancer import MixBalancerClient
from src.infra.clients.tournament_balancer import TournamentBalancerClient
from src.core.usecases.application import (
    GetApplicationUseCase,
    ListApplicationsUseCase,
    ReviewApplicationUseCase,
    SubmitApplicationUseCase,
)
from src.core.usecases.event import (
    ActivateEventUseCase,
    CancelEventUseCase,
    CompleteSingleGameEventUseCase,
    CloseRegistrationUseCase,
    CreateEventUseCase,
    GetEventUseCase,
    ListEventsUseCase,
    OpenRegistrationUseCase,
    UpdateEventUseCase,
)
from src.core.usecases.organizer import (
    AddOrganizerUseCase,
    ListOrganizersUseCase,
    RemoveOrganizerUseCase,
)
from src.core.usecases.player import (
    ListPlayersUseCase,
    RemovePlayerUseCase,
    UpdatePlayerStatusUseCase,
)
from src.core.usecases.draft import (
    CreateDraftUseCase,
    GetDraftUseCase,
    ListDraftsUseCase,
)
from src.core.usecases.team_formation import (
    RunTeamFormationUseCase,
    GetTeamFormationUseCase,
    ChooseTeamFormationVariantUseCase,
)
from src.core.usecases.team import ListTeamsUseCase
from src.core.usecases.match import GetMatchUseCase, ListMatchesUseCase, RecordSingleMatchResultUseCase, SingleMatchSetupUseCase
from src.core.usecases.settings import (
    AddIntegrationUseCase,
    RemoveIntegrationUseCase,
    AddGameRoleUseCase,
    UpdateGameRoleUseCase,
    RemoveGameRoleUseCase,
    AddCustomFieldUseCase,
    UpdateCustomFieldUseCase,
    RemoveCustomFieldUseCase,
    UpdateTimeSettingsUseCase,
    ListEventsUseCase,
    GetApplicationFormSettingsUseCase,
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

async def get_rating_client(
    broker: Annotated[RabbitBroker, Context()],
) -> RatingClient:
    return RatingClient(broker)


async def get_mix_balancer_client(
    broker: Annotated[RabbitBroker, Context()],
) -> MixBalancerClient:
    return MixBalancerClient(broker)


async def get_tournament_balancer_client(
    broker: Annotated[RabbitBroker, Context()],
) -> TournamentBalancerClient:
    return TournamentBalancerClient(broker)


# -- Store providers --

async def get_team_formation_variant_store(
    redis: RedisSession,
) -> TeamFormationVariantStore:
    return TeamFormationVariantStore(redis)


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

RatingClientDependency = Annotated[RatingClient, Depends(get_rating_client)]
MixBalancerClientDependency = Annotated[MixBalancerClient, Depends(get_mix_balancer_client)]
TournamentBalancerClientDependency = Annotated[TournamentBalancerClient, Depends(get_tournament_balancer_client)]

# -- Store type aliases --

TeamFormationVariantStoreDependency = Annotated[TeamFormationVariantStore, Depends(get_team_formation_variant_store)]

# -- Use case providers --

async def get_create_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    time_settings_repo: ApplicationTimeSettingsRepositoryDependency,
) -> CreateEventUseCase:
    return CreateEventUseCase(event_repo, organizer_repo, time_settings_repo)


async def get_get_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> GetEventUseCase:
    return GetEventUseCase(event_repo, organizer_repo)


async def get_list_events_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> ListEventsUseCase:
    return ListEventsUseCase(event_repo, organizer_repo)


async def get_update_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> UpdateEventUseCase:
    return UpdateEventUseCase(event_repo, organizer_repo)


async def get_activate_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> ActivateEventUseCase:
    return ActivateEventUseCase(event_repo, organizer_repo)


async def get_open_registration_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> OpenRegistrationUseCase:
    return OpenRegistrationUseCase(event_repo, organizer_repo)


async def get_close_registration_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> CloseRegistrationUseCase:
    return CloseRegistrationUseCase(event_repo, organizer_repo)


async def get_cancel_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> CancelEventUseCase:
    return CancelEventUseCase(event_repo, organizer_repo)


async def get_complete_single_game_event_use_case(
    event_repo: EventRepositoryDependency,
    match_repo: MatchRepositoryDependency,
) -> CompleteSingleGameEventUseCase:
    return CompleteSingleGameEventUseCase(event_repo, match_repo)


async def get_list_organizers_use_case(
    organizer_repo: OrganizerRepositoryDependency,
    event_repo: EventRepositoryDependency,
) -> ListOrganizersUseCase:
    return ListOrganizersUseCase(organizer_repo, event_repo)


async def get_add_organizer_use_case(
    organizer_repo: OrganizerRepositoryDependency,
    event_repo: EventRepositoryDependency,
) -> AddOrganizerUseCase:
    return AddOrganizerUseCase(organizer_repo, event_repo)


async def get_remove_organizer_use_case(
    organizer_repo: OrganizerRepositoryDependency,
    event_repo: EventRepositoryDependency,
) -> RemoveOrganizerUseCase:
    return RemoveOrganizerUseCase(organizer_repo, event_repo)


async def get_submit_application_use_case(
    event_repo: EventRepositoryDependency,
    application_repo: ApplicationRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    player_role_repo: PlayerRoleRepositoryDependency,
    filled_field_repo: FilledApplicationFieldRepositoryDependency,
    application_integration_repo: ApplicationIntegrationRepositoryDependency,
) -> SubmitApplicationUseCase:
    return SubmitApplicationUseCase(
        event_repo, application_repo, player_repo, player_role_repo,
        filled_field_repo, application_integration_repo,
    )


async def get_review_application_use_case(
    event_repo: EventRepositoryDependency,
    application_repo: ApplicationRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    player_role_repo: PlayerRoleRepositoryDependency,
) -> ReviewApplicationUseCase:
    return ReviewApplicationUseCase(event_repo, application_repo, player_repo, player_role_repo)


async def get_get_application_use_case(
    event_repo: EventRepositoryDependency,
    application_repo: ApplicationRepositoryDependency,
) -> GetApplicationUseCase:
    return GetApplicationUseCase(event_repo, application_repo)


async def get_list_applications_use_case(
    event_repo: EventRepositoryDependency,
    application_repo: ApplicationRepositoryDependency,
) -> ListApplicationsUseCase:
    return ListApplicationsUseCase(event_repo, application_repo)


async def get_list_players_use_case(
    event_repo: EventRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
) -> ListPlayersUseCase:
    return ListPlayersUseCase(event_repo, player_repo)


async def get_update_player_status_use_case(
    event_repo: EventRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
) -> UpdatePlayerStatusUseCase:
    return UpdatePlayerStatusUseCase(event_repo, player_repo)


async def get_remove_player_use_case(
    event_repo: EventRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
) -> RemovePlayerUseCase:
    return RemovePlayerUseCase(event_repo, player_repo)


# -- Stage 5 use case providers --

async def get_create_draft_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    drafted_player_repo: DraftedPlayerRepositoryDependency,
    match_repo: MatchRepositoryDependency,
) -> CreateDraftUseCase:
    return CreateDraftUseCase(event_repo, organizer_repo, player_repo, draft_repo, drafted_player_repo, match_repo)


async def get_get_draft_use_case(
    draft_repo: DraftRepositoryDependency,
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> GetDraftUseCase:
    return GetDraftUseCase(draft_repo, event_repo, organizer_repo)


async def get_list_drafts_use_case(
    draft_repo: DraftRepositoryDependency,
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> ListDraftsUseCase:
    return ListDraftsUseCase(draft_repo, event_repo, organizer_repo)


async def get_run_team_formation_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    variant_store: TeamFormationVariantStoreDependency,
    rating_client: RatingClientDependency,
    mix_balancer_client: MixBalancerClientDependency,
    tournament_balancer_client: TournamentBalancerClientDependency,
) -> RunTeamFormationUseCase:
    return RunTeamFormationUseCase(
        event_repo, organizer_repo, draft_repo, player_repo,
        team_repo, variant_store, rating_client, mix_balancer_client,
        tournament_balancer_client, env,
    )


async def get_get_team_formation_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    variant_store: TeamFormationVariantStoreDependency,
) -> GetTeamFormationUseCase:
    return GetTeamFormationUseCase(event_repo, organizer_repo, draft_repo, variant_store)


async def get_choose_team_formation_variant_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    team_player_repo: TeamPlayerRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    variant_store: TeamFormationVariantStoreDependency,
) -> ChooseTeamFormationVariantUseCase:
    return ChooseTeamFormationVariantUseCase(
        event_repo, organizer_repo, draft_repo, team_repo,
        team_player_repo, player_repo, variant_store,
    )


async def get_list_teams_use_case(
    team_repo: TeamRepositoryDependency,
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> ListTeamsUseCase:
    return ListTeamsUseCase(team_repo, event_repo, organizer_repo)


async def get_single_match_setup_use_case(
    event_repo: EventRepositoryDependency,
    bracket_repo: BracketRepositoryDependency,
    stage_repo: StageRepositoryDependency,
    stage_group_repo: StageGroupRepositoryDependency,
    match_repo: MatchRepositoryDependency,
    match_slot_repo: MatchSlotRepositoryDependency,
    match_score_repo: MatchScoreRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    draft_repo: DraftRepositoryDependency,
) -> SingleMatchSetupUseCase:
    return SingleMatchSetupUseCase(
        event_repo,
        bracket_repo,
        stage_repo,
        stage_group_repo,
        match_repo,
        match_slot_repo,
        match_score_repo,
        team_repo,
        draft_repo,
    )


async def get_record_single_match_result_use_case(
    event_repo: EventRepositoryDependency,
    match_repo: MatchRepositoryDependency,
    match_score_repo: MatchScoreRepositoryDependency,
    team_repo: TeamRepositoryDependency,
    player_repo: PlayerRepositoryDependency,
    rating_client: RatingClientDependency,
) -> RecordSingleMatchResultUseCase:
    return RecordSingleMatchResultUseCase(
        event_repo,
        match_repo,
        match_score_repo,
        team_repo,
        player_repo,
        rating_client,
        env,
    )


async def get_get_match_use_case(
    event_repo: EventRepositoryDependency,
    match_repo: MatchRepositoryDependency,
    team_repo: TeamRepositoryDependency,
) -> GetMatchUseCase:
    return GetMatchUseCase(event_repo, match_repo, team_repo)


async def get_list_matches_use_case(
    event_repo: EventRepositoryDependency,
    match_repo: MatchRepositoryDependency,
    team_repo: TeamRepositoryDependency,
) -> ListMatchesUseCase:
    return ListMatchesUseCase(event_repo, match_repo, team_repo)


# -- Settings use case providers --

async def get_add_integration_use_case(
    event_repo: EventRepositoryDependency,
    integration_repo: RequiredIntegrationRepositoryDependency,
) -> AddIntegrationUseCase:
    return AddIntegrationUseCase(event_repo, integration_repo)


async def get_remove_integration_use_case(
    event_repo: EventRepositoryDependency,
    integration_repo: RequiredIntegrationRepositoryDependency,
) -> RemoveIntegrationUseCase:
    return RemoveIntegrationUseCase(event_repo, integration_repo)


async def get_add_game_role_use_case(
    event_repo: EventRepositoryDependency,
    role_repo: SelectedGameRoleRepositoryDependency,
) -> AddGameRoleUseCase:
    return AddGameRoleUseCase(event_repo, role_repo)


async def get_update_game_role_use_case(
    event_repo: EventRepositoryDependency,
    role_repo: SelectedGameRoleRepositoryDependency,
) -> UpdateGameRoleUseCase:
    return UpdateGameRoleUseCase(event_repo, role_repo)


async def get_remove_game_role_use_case(
    event_repo: EventRepositoryDependency,
    role_repo: SelectedGameRoleRepositoryDependency,
) -> RemoveGameRoleUseCase:
    return RemoveGameRoleUseCase(event_repo, role_repo)


async def get_add_custom_field_use_case(
    event_repo: EventRepositoryDependency,
    field_repo: ApplicationCustomFieldRepositoryDependency,
) -> AddCustomFieldUseCase:
    return AddCustomFieldUseCase(event_repo, field_repo)


async def get_update_custom_field_use_case(
    event_repo: EventRepositoryDependency,
    field_repo: ApplicationCustomFieldRepositoryDependency,
) -> UpdateCustomFieldUseCase:
    return UpdateCustomFieldUseCase(event_repo, field_repo)


async def get_remove_custom_field_use_case(
    event_repo: EventRepositoryDependency,
    field_repo: ApplicationCustomFieldRepositoryDependency,
) -> RemoveCustomFieldUseCase:
    return RemoveCustomFieldUseCase(event_repo, field_repo)


async def get_update_time_settings_use_case(
    event_repo: EventRepositoryDependency,
    time_repo: ApplicationTimeSettingsRepositoryDependency,
) -> UpdateTimeSettingsUseCase:
    return UpdateTimeSettingsUseCase(event_repo, time_repo)


async def get_get_application_form_settings_use_case(
    event_repo: EventRepositoryDependency,
    integration_repo: RequiredIntegrationRepositoryDependency,
    role_repo: SelectedGameRoleRepositoryDependency,
    field_repo: ApplicationCustomFieldRepositoryDependency,
    time_repo: ApplicationTimeSettingsRepositoryDependency,
) -> GetApplicationFormSettingsUseCase:
    return GetApplicationFormSettingsUseCase(
        event_repo, integration_repo, role_repo, field_repo, time_repo
    )


# -- Use case type aliases --

CreateEventUseCaseDependency = Annotated[CreateEventUseCase, Depends(get_create_event_use_case)]
GetEventUseCaseDependency = Annotated[GetEventUseCase, Depends(get_get_event_use_case)]
ListEventsUseCaseDependency = Annotated[ListEventsUseCase, Depends(get_list_events_use_case)]
UpdateEventUseCaseDependency = Annotated[UpdateEventUseCase, Depends(get_update_event_use_case)]
ActivateEventUseCaseDependency = Annotated[ActivateEventUseCase, Depends(get_activate_event_use_case)]
OpenRegistrationUseCaseDependency = Annotated[OpenRegistrationUseCase, Depends(get_open_registration_use_case)]
CloseRegistrationUseCaseDependency = Annotated[CloseRegistrationUseCase, Depends(get_close_registration_use_case)]
CancelEventUseCaseDependency = Annotated[CancelEventUseCase, Depends(get_cancel_event_use_case)]
CompleteSingleGameEventUseCaseDependency = Annotated[
    CompleteSingleGameEventUseCase, Depends(get_complete_single_game_event_use_case)
]
ListOrganizersUseCaseDependency = Annotated[ListOrganizersUseCase, Depends(get_list_organizers_use_case)]
AddOrganizerUseCaseDependency = Annotated[AddOrganizerUseCase, Depends(get_add_organizer_use_case)]
RemoveOrganizerUseCaseDependency = Annotated[RemoveOrganizerUseCase, Depends(get_remove_organizer_use_case)]
SubmitApplicationUseCaseDependency = Annotated[SubmitApplicationUseCase, Depends(get_submit_application_use_case)]
ReviewApplicationUseCaseDependency = Annotated[ReviewApplicationUseCase, Depends(get_review_application_use_case)]
GetApplicationUseCaseDependency = Annotated[GetApplicationUseCase, Depends(get_get_application_use_case)]
ListApplicationsUseCaseDependency = Annotated[ListApplicationsUseCase, Depends(get_list_applications_use_case)]
ListPlayersUseCaseDependency = Annotated[ListPlayersUseCase, Depends(get_list_players_use_case)]
UpdatePlayerStatusUseCaseDependency = Annotated[UpdatePlayerStatusUseCase, Depends(get_update_player_status_use_case)]
RemovePlayerUseCaseDependency = Annotated[RemovePlayerUseCase, Depends(get_remove_player_use_case)]

# -- Settings use case type aliases --

AddIntegrationUseCaseDependency = Annotated[AddIntegrationUseCase, Depends(get_add_integration_use_case)]
RemoveIntegrationUseCaseDependency = Annotated[RemoveIntegrationUseCase, Depends(get_remove_integration_use_case)]
AddGameRoleUseCaseDependency = Annotated[AddGameRoleUseCase, Depends(get_add_game_role_use_case)]
UpdateGameRoleUseCaseDependency = Annotated[UpdateGameRoleUseCase, Depends(get_update_game_role_use_case)]
RemoveGameRoleUseCaseDependency = Annotated[RemoveGameRoleUseCase, Depends(get_remove_game_role_use_case)]
AddCustomFieldUseCaseDependency = Annotated[AddCustomFieldUseCase, Depends(get_add_custom_field_use_case)]
UpdateCustomFieldUseCaseDependency = Annotated[UpdateCustomFieldUseCase, Depends(get_update_custom_field_use_case)]
RemoveCustomFieldUseCaseDependency = Annotated[RemoveCustomFieldUseCase, Depends(get_remove_custom_field_use_case)]
UpdateTimeSettingsUseCaseDependency = Annotated[UpdateTimeSettingsUseCase, Depends(get_update_time_settings_use_case)]
GetApplicationFormSettingsUseCaseDependency = Annotated[GetApplicationFormSettingsUseCase, Depends(get_get_application_form_settings_use_case)]

# -- Stage 5 use case type aliases --

CreateDraftUseCaseDependency = Annotated[CreateDraftUseCase, Depends(get_create_draft_use_case)]
GetDraftUseCaseDependency = Annotated[GetDraftUseCase, Depends(get_get_draft_use_case)]
ListDraftsUseCaseDependency = Annotated[ListDraftsUseCase, Depends(get_list_drafts_use_case)]
RunTeamFormationUseCaseDependency = Annotated[RunTeamFormationUseCase, Depends(get_run_team_formation_use_case)]
GetTeamFormationUseCaseDependency = Annotated[GetTeamFormationUseCase, Depends(get_get_team_formation_use_case)]
ChooseTeamFormationVariantUseCaseDependency = Annotated[
    ChooseTeamFormationVariantUseCase, Depends(get_choose_team_formation_variant_use_case)
]
ListTeamsUseCaseDependency = Annotated[ListTeamsUseCase, Depends(get_list_teams_use_case)]
SingleMatchSetupUseCaseDependency = Annotated[SingleMatchSetupUseCase, Depends(get_single_match_setup_use_case)]
RecordSingleMatchResultUseCaseDependency = Annotated[
    RecordSingleMatchResultUseCase, Depends(get_record_single_match_result_use_case)
]
GetMatchUseCaseDependency = Annotated[GetMatchUseCase, Depends(get_get_match_use_case)]
ListMatchesUseCaseDependency = Annotated[ListMatchesUseCase, Depends(get_list_matches_use_case)]
