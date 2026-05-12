from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.application import GetApplicationCommand, ListApplicationsCommand
from src.core.exceptions import ForbiddenException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_VIEW
from src.core.models.application import Application, ApplicationStatus
from src.core.models.event import Event, EventMatchType, EventStatus, TeamFormation
from src.core.models.organizer import Organizer
from src.core.services.application import ApplicationService


class EventRepo:
    def __init__(self, event: Event):
        self.event = event

    async def get(self, field_id, **_kwargs):
        return self.event if field_id == self.event.id else None


class ApplicationRepo:
    def __init__(self, application: Application):
        self.application = application

    async def get(self, field_id, **_kwargs):
        return self.application if field_id == self.application.id else None

    async def list_by_event(self, event_id, **_kwargs):
        return [self.application] if event_id == self.application.event_id else []


def make_event(server_id, *, is_public=False, organizer_member_id=None):
    event_id = uuid4()
    organizers = []
    if organizer_member_id:
        organizers.append(
            Organizer(id=uuid4(), event_id=event_id, member_id=organizer_member_id)
        )

    return Event(
        id=event_id,
        name="Test Event",
        match_type=EventMatchType.SINGLE,
        use_application=True,
        is_public=is_public,
        team_size=5,
        team_formation=TeamFormation.BALANCE,
        status=EventStatus.CREATED,
        allow_multiple_drafts=False,
        server_id=server_id,
        organizers=organizers,
    )


def make_application(event_id):
    return Application(
        id=uuid4(),
        event_id=event_id,
        member_id=uuid4(),
        is_approved=False,
        status=ApplicationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )


def make_service(event, application):
    return ApplicationService(
        event_repo=EventRepo(event),
        application_repo=ApplicationRepo(application),
        player_repo=object(),
        player_role_repo=object(),
        filled_field_repo=object(),
        application_integration_repo=object(),
    )


@pytest.mark.parametrize(
    ("is_public", "permission_mask"),
    [
        (True, 0),
        (False, P_EVENT_ADMIN_VIEW),
    ],
)
async def test_list_applications_allows_event_viewers(is_public, permission_mask):
    server_id = uuid4()
    event = make_event(server_id, is_public=is_public)
    application = make_application(event.id)
    service = make_service(event, application)

    result = await service.get_list(
        ListApplicationsCommand(
            event_id=event.id,
            access_data=AccessDataRequest(
                member_id=uuid4(),
                server_id=server_id,
                permission_mask=permission_mask,
                restriction_mask=0,
            ),
        )
    )

    assert len(result) == 1
    assert result[0].id == application.id


async def test_get_application_allows_event_viewer():
    server_id = uuid4()
    event = make_event(server_id, is_public=True)
    application = make_application(event.id)
    service = make_service(event, application)

    result = await service.get(
        GetApplicationCommand(
            application_id=application.id,
            access_data=AccessDataRequest(
                member_id=uuid4(),
                server_id=server_id,
                permission_mask=0,
                restriction_mask=0,
            ),
        )
    )

    assert result["id"] == str(application.id)


async def test_list_applications_rejects_private_event_non_viewer():
    server_id = uuid4()
    event = make_event(server_id, is_public=False)
    application = make_application(event.id)
    service = make_service(event, application)

    with pytest.raises(ForbiddenException):
        await service.get_list(
            ListApplicationsCommand(
                event_id=event.id,
                access_data=AccessDataRequest(
                    member_id=uuid4(),
                    server_id=server_id,
                    permission_mask=0,
                    restriction_mask=0,
                ),
            )
        )
