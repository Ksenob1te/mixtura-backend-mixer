# from faststream import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import AsyncGenerator
# from src.infra.postgre.engine import DatabaseSessionManager, connect_string
# # Repositories
# from src.infra.postgre.repo import (
#     ApplicationRepository, ApplicationCustomFieldRepository, ApplicationIntegrationRepository,
#     ApplicationTimeSettingsRepository,
#     BracketPlacementRepository, BracketRepository, DraftRepository, DraftedPlayerRepository, EventRepository,
#     FilledApplicationFieldRepository, MatchScoreRepository, MatchSlotRepository, MatchRepository, OrganizerRepository,
#     PlayerRepository, PlayerRoleRepository, RequiredIntegrationRepository, RoundRobinSettingsRepository,
#     SelectedGameRoleRepository, StageGroupRepository, StageRepository, SwissSettingsRepository,
#     TeamPlayerRepository, TeamRepository
# )
# # Services
# from src.domain.service.application import ApplicationService
# from src.domain.service.draft import DraftService
# from src.domain.service.event import EventService
# from src.domain.service.match import MatchService
# from src.domain.service.team import TeamService
# from src.domain.service.tournament import TournamentService
#
# db_manager = DatabaseSessionManager(connect_string)
#
#
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     async with db_manager.session() as session:
#         yield session
#
#
# def get_application_repo(session: AsyncSession = Depends(get_session)) -> ApplicationRepository:
#     return ApplicationRepository(session)
#
#
# def get_event_repo(session: AsyncSession = Depends(get_session)) -> EventRepository:
#     return EventRepository(session)
#
#
# def get_organizer_repo(session: AsyncSession = Depends(get_session)) -> OrganizerRepository:
#     return OrganizerRepository(session)
#
#
# def get_required_integration_repo(session: AsyncSession = Depends(get_session)) -> RequiredIntegrationRepository:
#     return RequiredIntegrationRepository(session)
#
#
# def get_application_time_settings_repo(
#         session: AsyncSession = Depends(get_session)) -> ApplicationTimeSettingsRepository:
#     return ApplicationTimeSettingsRepository(session)
#
#
# def get_selected_game_role_repo(session: AsyncSession = Depends(get_session)) -> SelectedGameRoleRepository:
#     return SelectedGameRoleRepository(session)
#
#
# def get_application_custom_field_repo(session: AsyncSession = Depends(get_session)) -> ApplicationCustomFieldRepository:
#     return ApplicationCustomFieldRepository(session)
#
#
# def get_event_service(
#         event_repo: EventRepository = Depends(get_event_repo),
#         organizer_repo: OrganizerRepository = Depends(get_organizer_repo),
#         req_integ_repo: RequiredIntegrationRepository = Depends(get_required_integration_repo),
#         time_settings_repo: ApplicationTimeSettingsRepository = Depends(get_application_time_settings_repo),
#         game_role_repo: SelectedGameRoleRepository = Depends(get_selected_game_role_repo),
#         custom_field_repo: ApplicationCustomFieldRepository = Depends(get_application_custom_field_repo)
# ) -> EventService:
#     return EventService(event_repo, organizer_repo, req_integ_repo, time_settings_repo, game_role_repo,
#                         custom_field_repo)
# # (Other repos and services are omitted for brevity, but this serves as the foundational dependency setup)
