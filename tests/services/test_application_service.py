from uuid import uuid4

import pytest

from src.core.commands.application import (
    FilledFieldPayload,
    GetApplicationCommand,
    IntegrationPayload,
    ListApplicationsCommand,
    ReviewApplicationCommand,
    RolePriorityPayload,
    SubmitApplicationCommand,
)
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException
from src.core.interfaces.repo.access import R_MIX_BAN, R_TOURNAMENT_BAN
from src.core.models.application import ApplicationStatus, ApplicationCreate
from src.core.models.application_custom_field import ApplicationCustomFieldCreate
from src.core.models.required_integration import RequiredIntegrationCreate
from src.core.models.event import EventCreate, EventMatchType, EventStatus, TeamFormation
from src.core.models.organizer import OrganizerCreate
from src.core.models.selected_game_role import SelectedGameRoleCreate

pytestmark = pytest.mark.asyncio


class TestApplicationService:
    async def test_submit_creates_application_player_fields_integrations_and_roles(
            self,
            application_service,
            event_repo,
            application_custom_field_repo,
            required_integration_repo,
            selected_game_role_repo,
            application_repo,
            player_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.DRAFT,
                allow_multiple_drafts=False,
            )
        )
        field = await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(
                event_id=event.id,
                name="Discord",
                is_required=True,
                is_private=False,
            )
        )
        await required_integration_repo.create(RequiredIntegrationCreate(event_id=event.id, provider_id=uuid4()))
        selected_role = await selected_game_role_repo.create(
            SelectedGameRoleCreate(event_id=event.id, game_role_id=uuid4())
        )

        result = await application_service.submit(
            SubmitApplicationCommand(
                event_id=event.id,
                access_data=AccessDataRequest(
                    server_id=server_id,
                    member_id=member_id,
                    permission_mask=2 ** 32 - 1,
                    restriction_mask=0
                ),
                filled_fields=[
                    FilledFieldPayload(custom_field_id=field.id, value="tester#1234")
                ],
                integrations=[
                    IntegrationPayload(
                        integration_id=uuid4(),
                        provider_id=uuid4(),
                        provider_name="discord",
                    )
                ],
                role_priorities=[
                    RolePriorityPayload(role_id=selected_role.game_role_id, priority=1)
                ],
            )
        )

        application = await application_repo.get(result.id)
        player = await player_repo.get(result.player_id, load_roles=True)

        assert result.status == ApplicationStatus.PENDING
        assert result.auto_approved is False
        assert application is not None
        assert application.member_id == member_id
        assert len(application.filled_fields) == 1
        assert application.filled_fields[0].value == "tester#1234"
        assert len(application.integrations) == 1
        assert application.integrations[0].provider_name == "discord"
        assert player is not None
        assert player.application_id == application.id
        assert len(player.player_roles) == 1
        assert player.player_roles[0].game_role_id == selected_role.id

    async def test_submit_auto_approves_when_event_does_not_use_applications(
            self,
            application_service,
            event_repo,
            application_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                status=EventStatus.IDLE,
                match_type=EventMatchType.SINGLE,
                use_application=False,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.DRAFT,
                allow_multiple_drafts=False,
            )
        )

        result = await application_service.submit(
            SubmitApplicationCommand(
                event_id=event.id,
                access_data=AccessDataRequest(
                    server_id=server_id,
                    member_id=member_id,
                    permission_mask=2 ** 32 - 1,
                    restriction_mask=0
                ),
            )
        )

        application = await application_repo.get(result.id)
        assert result.status == ApplicationStatus.APPROVED
        assert result.auto_approved is True
        assert application is not None

    async def test_submit_rejects_duplicate_application_for_member(
            self,
            application_service,
            event_repo,
            application_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.DRAFT,
                allow_multiple_drafts=False,
            )
        )
        await application_repo.create(
            ApplicationCreate(
                event_id=event.id,
                member_id=member_id,
                status=ApplicationStatus.PENDING,
            )
        )

        with pytest.raises(ConflictException):
            await application_service.submit(
                SubmitApplicationCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(
                        server_id=server_id,
                        member_id=member_id,
                        permission_mask=2 ** 32 - 1,
                        restriction_mask=0
                    ),
                )
            )

    async def test_review_approve_updates_application_and_creates_player(
            self,
            application_service,
            event_repo,
            application_repo,
            player_repo,
            organizer_repo,
            server_id,
            organizer_id,
    ):
        applicant_id = uuid4()
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        await organizer_repo.create(
            OrganizerCreate(event_id=event.id, member_id=organizer_id)
        )
        application = await application_repo.create(
            {
                "event_id": event.id,
                "member_id": applicant_id,
                "status": ApplicationStatus.PENDING,
            }
        )

        result = await application_service.review(
            ReviewApplicationCommand(
                application_id=application.id,
                status=ApplicationStatus.APPROVED,
                access_data=AccessDataRequest(
                    server_id=server_id,
                    member_id=organizer_id,
                ),
            )
        )

        stored = await application_repo.get(result.id)
        player = await player_repo.get(result.player_id)
        assert result.status == ApplicationStatus.APPROVED
        assert stored is not None
        assert player is not None
        assert player.member_id == applicant_id

    async def test_get_allows_owner_on_private_event(
            self,
            application_service,
            event_repo,
            application_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                is_public=False,
                status=EventStatus.CREATED,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        application = await application_repo.create(
            {
                "event_id": event.id,
                "member_id": member_id,
                "status": ApplicationStatus.PENDING,
            }
        )

        result = await application_service.get(
            GetApplicationCommand(
                application_id=application.id,
                access_data=AccessDataRequest(server_id=server_id, member_id=member_id),
            )
        )

        assert result.id == application.id

    async def test_get_list_allows_private_event_organizer(
            self,
            application_service,
            event_repo,
            application_repo,
            organizer_repo,
            server_id,
            member_id,
    ):
        private_event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Private",
                is_public=False,
                status=EventStatus.CREATED,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        await organizer_repo.create(
            OrganizerCreate(event_id=private_event.id, member_id=member_id)
        )
        private_application = await application_repo.create(
            {
                "event_id": private_event.id,
                "member_id": member_id,
                "status": ApplicationStatus.PENDING,
            }
        )

        result = await application_service.get_list(
            ListApplicationsCommand(
                event_id=private_event.id,
                access_data=AccessDataRequest(server_id=server_id, member_id=member_id),
            )
        )

        assert [item.id for item in result] == [private_application.id]

    async def test_get_list_rejects_private_event_non_viewer(
            self,
            application_service,
            event_repo,
            application_repo,
            server_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                is_public=False,
                status=EventStatus.CREATED,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        await application_repo.create(
            {
                "event_id": event.id,
                "member_id": uuid4(),
                "status": ApplicationStatus.PENDING,
            }
        )

        with pytest.raises(ForbiddenException):
            await application_service.get_list(
                ListApplicationsCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=server_id),
                )
            )

    async def test_submit_rejects_mix_ban_for_single_event(
            self,
            application_service,
            event_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Single",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )

        with pytest.raises(ForbiddenException):
            await application_service.submit(
                SubmitApplicationCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(
                        server_id=server_id,
                        member_id=member_id,
                        restriction_mask=R_MIX_BAN,
                    ),
                )
            )

    async def test_submit_rejects_tournament_ban_for_tournament_event(
            self,
            application_service,
            event_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Tournament",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.TOURNAMENT,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )

        with pytest.raises(ForbiddenException):
            await application_service.submit(
                SubmitApplicationCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(
                        server_id=server_id,
                        member_id=member_id,
                        restriction_mask=R_TOURNAMENT_BAN,
                    ),
                )
            )

    async def test_submit_rejects_missing_required_custom_field(
            self,
            application_service,
            event_repo,
            application_custom_field_repo,
            server_id,
            member_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="WithField",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        await application_custom_field_repo.create(
            ApplicationCustomFieldCreate(
                event_id=event.id,
                name="Required",
                is_required=True,
                is_private=False,
            )
        )

        with pytest.raises(BadRequestException):
            await application_service.submit(
                SubmitApplicationCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=member_id),
                )
            )

    async def test_review_waitlist_updates_status(
            self,
            application_service,
            event_repo,
            application_repo,
            organizer_repo,
            server_id,
            organizer_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Event",
                status=EventStatus.REGISTRATION,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=organizer_id))
        application = await application_repo.create(
            {
                "event_id": event.id,
                "member_id": uuid4(),
                "status": ApplicationStatus.PENDING,
            }
        )

        result = await application_service.review(
            ReviewApplicationCommand(
                application_id=application.id,
                status=ApplicationStatus.WAITLIST,
                access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
            )
        )

        stored = await application_repo.get(application.id)
        assert result.status == ApplicationStatus.WAITLIST
        assert stored is not None
        assert stored.status == ApplicationStatus.WAITLIST

    async def test_get_rejects_non_owner_on_private_event(
            self,
            application_service,
            event_repo,
            application_repo,
            server_id,
    ):
        event = await event_repo.create(
            EventCreate(
                server_id=server_id,
                name="Private",
                is_public=False,
                status=EventStatus.CREATED,
                match_type=EventMatchType.SINGLE,
                use_application=True,
                team_size=5,
                team_formation=0,
                allow_multiple_drafts=False,
            )
        )
        application = await application_repo.create(
            {
                "event_id": event.id,
                "member_id": uuid4(),
                "status": ApplicationStatus.PENDING,
            }
        )

        with pytest.raises(ForbiddenException):
            await application_service.get(
                GetApplicationCommand(
                    application_id=application.id,
                    access_data=AccessDataRequest(server_id=server_id, member_id=uuid4()),
                )
            )
