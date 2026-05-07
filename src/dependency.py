from typing import Annotated, Any

from faststream import Context, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.core.usecases.application import (
    GetApplicationUseCase,
    ListApplicationsUseCase,
    ReviewApplicationUseCase,
    SubmitApplicationUseCase,
)
from src.core.usecases.event import (
    ActivateEventUseCase,
    CancelEventUseCase,
    CloseRegistrationUseCase,
    CreateEventUseCase,
    GetEventUseCase,
    ListPrivateEventsUseCase,
    ListPublicEventsUseCase,
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


async def get_db_session(
    session_manager: Annotated[DatabaseSessionManager, Context()],
):
    async with session_manager.session() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_event_repository(session: DatabaseSession) -> Any:
    return EventRepository(session)  # type: ignore[abstract]


async def get_organizer_repository(session: DatabaseSession) -> Any:
    return OrganizerRepository(session)  # type: ignore[abstract]


async def get_application_repository(session: DatabaseSession) -> Any:
    return ApplicationRepository(session)  # type: ignore[abstract]


async def get_application_custom_field_repository(session: DatabaseSession) -> Any:
    return ApplicationCustomFieldRepository(session)  # type: ignore[abstract]


async def get_application_integration_repository(session: DatabaseSession) -> Any:
    return ApplicationIntegrationRepository(session)  # type: ignore[abstract]


async def get_application_time_settings_repository(session: DatabaseSession) -> Any:
    return ApplicationTimeSettingsRepository(session)  # type: ignore[abstract]


async def get_bracket_repository(session: DatabaseSession) -> Any:
    return BracketRepository(session)  # type: ignore[abstract]


async def get_bracket_placement_repository(session: DatabaseSession) -> Any:
    return BracketPlacementRepository(session)  # type: ignore[abstract]


async def get_draft_repository(session: DatabaseSession) -> Any:
    return DraftRepository(session)  # type: ignore[abstract]


async def get_drafted_player_repository(session: DatabaseSession) -> Any:
    return DraftedPlayerRepository(session)  # type: ignore[abstract]


async def get_filled_application_field_repository(session: DatabaseSession) -> Any:
    return FilledApplicationFieldRepository(session)  # type: ignore[abstract]


async def get_match_repository(session: DatabaseSession) -> Any:
    return MatchRepository(session)  # type: ignore[abstract]


async def get_match_score_repository(session: DatabaseSession) -> Any:
    return MatchScoreRepository(session)  # type: ignore[abstract]


async def get_match_slot_repository(session: DatabaseSession) -> Any:
    return MatchSlotRepository(session)  # type: ignore[abstract]


async def get_player_repository(session: DatabaseSession) -> Any:
    return PlayerRepository(session)  # type: ignore[abstract]


async def get_player_role_repository(session: DatabaseSession) -> Any:
    return PlayerRoleRepository(session)  # type: ignore[abstract]


async def get_required_integration_repository(session: DatabaseSession) -> Any:
    return RequiredIntegrationRepository(session)  # type: ignore[abstract]


async def get_round_robin_settings_repository(session: DatabaseSession) -> Any:
    return RoundRobinSettingsRepository(session)  # type: ignore[abstract]


async def get_selected_game_role_repository(session: DatabaseSession) -> Any:
    return SelectedGameRoleRepository(session)  # type: ignore[abstract]


async def get_stage_repository(session: DatabaseSession) -> Any:
    return StageRepository(session)  # type: ignore[abstract]


async def get_stage_group_repository(session: DatabaseSession) -> Any:
    return StageGroupRepository(session)  # type: ignore[abstract]


async def get_swiss_settings_repository(session: DatabaseSession) -> Any:
    return SwissSettingsRepository(session)  # type: ignore[abstract]


async def get_team_repository(session: DatabaseSession) -> Any:
    return TeamRepository(session)  # type: ignore[abstract]


async def get_team_player_repository(session: DatabaseSession) -> Any:
    return TeamPlayerRepository(session)  # type: ignore[abstract]


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

# -- Use case providers --

async def get_create_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> CreateEventUseCase:
    return CreateEventUseCase(event_repo, organizer_repo)


async def get_get_event_use_case(
    event_repo: EventRepositoryDependency,
    organizer_repo: OrganizerRepositoryDependency,
) -> GetEventUseCase:
    return GetEventUseCase(event_repo, organizer_repo)


async def get_list_public_events_use_case(
    event_repo: EventRepositoryDependency,
) -> ListPublicEventsUseCase:
    return ListPublicEventsUseCase(event_repo)


async def get_list_private_events_use_case(
    event_repo: EventRepositoryDependency,
) -> ListPrivateEventsUseCase:
    return ListPrivateEventsUseCase(event_repo)


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


CreateEventUseCaseDependency = Annotated[CreateEventUseCase, Depends(get_create_event_use_case)]
GetEventUseCaseDependency = Annotated[GetEventUseCase, Depends(get_get_event_use_case)]
ListPublicEventsUseCaseDependency = Annotated[ListPublicEventsUseCase, Depends(get_list_public_events_use_case)]
ListPrivateEventsUseCaseDependency = Annotated[ListPrivateEventsUseCase, Depends(get_list_private_events_use_case)]
UpdateEventUseCaseDependency = Annotated[UpdateEventUseCase, Depends(get_update_event_use_case)]
ActivateEventUseCaseDependency = Annotated[ActivateEventUseCase, Depends(get_activate_event_use_case)]
OpenRegistrationUseCaseDependency = Annotated[OpenRegistrationUseCase, Depends(get_open_registration_use_case)]
CloseRegistrationUseCaseDependency = Annotated[CloseRegistrationUseCase, Depends(get_close_registration_use_case)]
CancelEventUseCaseDependency = Annotated[CancelEventUseCase, Depends(get_cancel_event_use_case)]
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
