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
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_VIEW
from src.core.models.application import ApplicationStatus
from src.core.models.event import EventMatchType, EventStatus
from src.core.services.application import ApplicationService
from tests.services.helpers import (
    InMemoryApplicationIntegrationRepository,
    InMemoryApplicationRepository,
    InMemoryEventRepository,
    InMemoryFilledApplicationFieldRepository,
    InMemoryPlayerRepository,
    InMemoryPlayerRoleRepository,
    make_access,
    make_application,
    make_custom_field,
    make_event,
    make_event_player,
    make_required_integration,
    make_selected_game_role,
)

pytestmark = pytest.mark.asyncio


def make_service(events, applications=None, players=None):
    event_repo = InMemoryEventRepository(events)
    application_repo = InMemoryApplicationRepository(event_repo, applications or [])
    player_repo = InMemoryPlayerRepository(event_repo, application_repo, players or [])
    player_role_repo = InMemoryPlayerRoleRepository(player_repo)
    filled_field_repo = InMemoryFilledApplicationFieldRepository(application_repo)
    application_integration_repo = InMemoryApplicationIntegrationRepository(application_repo)
    service = ApplicationService(
        event_repo=event_repo,
        application_repo=application_repo,
        player_repo=player_repo,
        player_role_repo=player_role_repo,
        filled_field_repo=filled_field_repo,
        application_integration_repo=application_integration_repo,
    )
    return service, application_repo, player_repo, player_role_repo


async def test_submit_creates_pending_application_player_fields_integrations_and_roles():
    server_id = uuid4()
    member_id = uuid4()
    field = make_custom_field(uuid4(), name="Discord", is_required=True)
    integration = make_required_integration(field.event_id, name="discord")
    selected_role = make_selected_game_role(field.event_id)
    event = make_event(
        id=field.event_id,
        server_id=server_id,
        status=EventStatus.REGISTRATION,
        use_application=True,
        custom_fields=[field],
        required_integrations=[integration],
        selected_game_roles=[selected_role],
    )
    service, application_repo, player_repo, _player_role_repo = make_service([event])

    result = await service.submit(
        SubmitApplicationCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, member_id=member_id),
            filled_fields=[FilledFieldPayload(custom_field_id=field.id, value="tester#1234")],
            integrations=[
                IntegrationPayload(
                    integration_id=uuid4(),
                    provider_id=uuid4(),
                    provider_name="discord",
                )
            ],
            role_priorities=[RolePriorityPayload(role_id=selected_role.game_role_id, priority=1)],
        )
    )

    application = await application_repo.get(result.id)
    player = await player_repo.get(result.player_id)

    assert result.status == ApplicationStatus.PENDING
    assert result.auto_approved is False
    assert application is not None
    assert application.member_id == member_id
    assert application.filled_fields[0].value == "tester#1234"
    assert application.integrations[0].provider_name == "discord"
    assert player is not None
    assert player.application_id == application.id
    assert player.player_roles[0].game_role_id == selected_role.id


async def test_submit_auto_approves_when_event_does_not_use_applications():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, status=EventStatus.IDLE, use_application=False)
    service, application_repo, _player_repo, _player_role_repo = make_service([event])

    result = await service.submit(
        SubmitApplicationCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, member_id=member_id),
        )
    )

    application = await application_repo.get(result.id)
    assert result.status == ApplicationStatus.APPROVED
    assert result.auto_approved is True
    assert application is not None
    assert application.is_approved is True


async def test_submit_rejects_duplicate_application_for_member():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, status=EventStatus.REGISTRATION)
    application = make_application(event.id, member_id=member_id)
    service, _application_repo, _player_repo, _player_role_repo = make_service([event], [application])

    with pytest.raises(ConflictException):
        await service.submit(
            SubmitApplicationCommand(
                event_id=event.id,
                access_data=make_access(server_id=server_id, member_id=member_id),
            )
        )


async def test_submit_rejects_missing_required_custom_field():
    server_id = uuid4()
    field = make_custom_field(uuid4(), is_required=True)
    event = make_event(
        id=field.event_id,
        server_id=server_id,
        status=EventStatus.REGISTRATION,
        custom_fields=[field],
    )
    service, _application_repo, _player_repo, _player_role_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.submit(
            SubmitApplicationCommand(
                event_id=event.id,
                access_data=make_access(server_id=server_id),
            )
        )


async def test_submit_rejects_mix_banned_member_for_single_event():
    server_id = uuid4()
    event = make_event(
        server_id=server_id,
        status=EventStatus.REGISTRATION,
        match_type=EventMatchType.SINGLE,
    )
    service, _application_repo, _player_repo, _player_role_repo = make_service([event])

    with pytest.raises(ForbiddenException):
        await service.submit(
            SubmitApplicationCommand(
                event_id=event.id,
                access_data=make_access(server_id=server_id, restriction_mask=1 << 1),
            )
        )


async def test_review_approve_updates_application_and_creates_player():
    server_id = uuid4()
    organizer_id = uuid4()
    applicant_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], status=EventStatus.REGISTRATION)
    application = make_application(event.id, member_id=applicant_id)
    service, application_repo, player_repo, _player_role_repo = make_service([event], [application])

    result = await service.review(
        ReviewApplicationCommand(
            application_id=application.id,
            status=ApplicationStatus.APPROVED,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    stored = await application_repo.get(application.id)
    player = await player_repo.get(result.player_id)
    assert result.status == ApplicationStatus.APPROVED
    assert stored is not None
    assert stored.is_approved is True
    assert player is not None
    assert player.member_id == applicant_id


async def test_review_reject_deletes_existing_event_player():
    server_id = uuid4()
    organizer_id = uuid4()
    applicant_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], status=EventStatus.REGISTRATION)
    application = make_application(event.id, member_id=applicant_id)
    player = make_event_player(event.id, member_id=applicant_id, application_id=application.id)
    application = application.model_copy(update={"event_player": player})
    service, application_repo, player_repo, _player_role_repo = make_service([event], [application], [player])

    result = await service.review(
        ReviewApplicationCommand(
            application_id=application.id,
            status=ApplicationStatus.REJECTED,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    stored = await application_repo.get(application.id)
    assert result.status == ApplicationStatus.REJECTED
    assert player.id not in player_repo.players
    assert stored is not None
    assert stored.event_player is None


async def test_review_rejects_non_organizer_without_admin_permission():
    server_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[uuid4()])
    application = make_application(event.id)
    service, _application_repo, _player_repo, _player_role_repo = make_service([event], [application])

    with pytest.raises(ForbiddenException):
        await service.review(
            ReviewApplicationCommand(
                application_id=application.id,
                status=ApplicationStatus.APPROVED,
                access_data=make_access(server_id=server_id),
            )
        )


async def test_get_application_allows_owner_on_private_event():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, is_public=False, organizer_member_ids=[uuid4()])
    application = make_application(event.id, member_id=member_id)
    service, _application_repo, _player_repo, _player_role_repo = make_service([event], [application])

    result = await service.get(
        GetApplicationCommand(
            application_id=application.id,
            access_data=make_access(server_id=server_id, member_id=member_id),
        )
    )

    assert result.id == application.id


@pytest.mark.parametrize(
    ("is_public", "permission_mask"),
    [
        (True, 0),
        (False, P_EVENT_ADMIN_VIEW),
    ],
)
async def test_list_applications_allows_event_viewers(is_public, permission_mask):
    server_id = uuid4()
    event = make_event(server_id=server_id, is_public=is_public)
    application = make_application(event.id)
    service, _application_repo, _player_repo, _player_role_repo = make_service([event], [application])

    result = await service.get_list(
        ListApplicationsCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, permission_mask=permission_mask),
        )
    )

    assert [item.id for item in result] == [application.id]


async def test_list_applications_rejects_private_event_non_viewer():
    server_id = uuid4()
    event = make_event(server_id=server_id, is_public=False, organizer_member_ids=[uuid4()])
    application = make_application(event.id)
    service, _application_repo, _player_repo, _player_role_repo = make_service([event], [application])

    with pytest.raises(ForbiddenException):
        await service.get_list(
            ListApplicationsCommand(event_id=event.id, access_data=make_access(server_id=server_id))
        )
