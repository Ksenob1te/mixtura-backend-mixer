from uuid import uuid4

import pytest

from src.core.commands.event import (
    CancelEventCommand,
    CompleteEventCommand,
    CreateEventCommand,
    GetEventCommand,
    ListEventsCommand,
    UpdateEventCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException
from src.core.interfaces.repo.access import P_EVENT_CREATE
from src.core.models.event import EventMatchType, EventStatus, TeamFormation
from src.core.services.event import EventService
from tests.services.helpers import (
    InMemoryEventRepository,
    InMemoryMatchRepository,
    InMemoryOrganizerRepository,
    InMemoryTimeSettingsRepository,
    make_access,
    make_event,
)

pytestmark = pytest.mark.asyncio


def make_service(events=None, *, incomplete_count: int = 0):
    event_repo = InMemoryEventRepository(events or [])
    organizer_repo = InMemoryOrganizerRepository(event_repo)
    time_repo = InMemoryTimeSettingsRepository(event_repo)
    match_repo = InMemoryMatchRepository(incomplete_count=incomplete_count)
    service = EventService(
        event_repo=event_repo,
        organizer_repo=organizer_repo,
        time_settings_repo=time_repo,
        match_repo=match_repo,
    )
    return service, event_repo, organizer_repo, time_repo


async def test_create_event_creates_owner_organizer_and_time_settings():
    server_id = uuid4()
    member_id = uuid4()
    service, event_repo, organizer_repo, time_repo = make_service()

    result = await service.create(
        CreateEventCommand(
            access_data=make_access(
                server_id=server_id,
                member_id=member_id,
                permission_mask=P_EVENT_CREATE,
            ),
            name="Spring Mix",
            match_type=EventMatchType.SINGLE,
            use_application=True,
            is_public=True,
            team_size=5,
            team_formation=TeamFormation.BALANCE,
            allow_multiple_drafts=False,
        )
    )

    stored = await event_repo.get(result.id)

    assert stored is not None
    assert result.name == "Spring Mix"
    assert result.server_id == server_id
    assert [organizer.member_id for organizer in result.organizers] == [member_id]
    assert result.time_settings is not None
    assert await organizer_repo.list_by_event(result.id)
    assert await time_repo.get_by_event_id(result.id) is not None


async def test_create_event_requires_member_and_permission():
    service, _event_repo, _organizer_repo, _time_repo = make_service()

    with pytest.raises(ForbiddenException):
        await service.create(
            CreateEventCommand(
                access_data=make_access(permission_mask=P_EVENT_CREATE, anonymous=True),
                name="No Owner",
                match_type=EventMatchType.SINGLE,
                use_application=False,
                is_public=True,
                team_size=2,
                team_formation=TeamFormation.MANUAL,
                allow_multiple_drafts=False,
            )
        )

    with pytest.raises(ForbiddenException):
        await service.create(
            CreateEventCommand(
                access_data=make_access(),
                name="No Permission",
                match_type=EventMatchType.SINGLE,
                use_application=False,
                is_public=True,
                team_size=2,
                team_formation=TeamFormation.MANUAL,
                allow_multiple_drafts=False,
            )
        )


async def test_get_rejects_different_server():
    event = make_event(server_id=uuid4())
    service, _event_repo, _organizer_repo, _time_repo = make_service([event])

    with pytest.raises(ForbiddenException):
        await service.get(GetEventCommand(event_id=event.id, access_data=make_access(server_id=uuid4())))


async def test_get_list_shows_public_and_own_private_events_without_admin_permission():
    server_id = uuid4()
    member_id = uuid4()
    public_event = make_event(server_id=server_id, is_public=True, name="Public")
    own_private_event = make_event(
        server_id=server_id,
        is_public=False,
        name="Own Private",
        organizer_member_ids=[member_id],
    )
    other_private_event = make_event(server_id=server_id, is_public=False, name="Other Private")
    service, _event_repo, _organizer_repo, _time_repo = make_service(
        [public_event, own_private_event, other_private_event]
    )

    result = await service.get_list(
        ListEventsCommand(
            server_id=server_id,
            access_data=make_access(server_id=server_id, member_id=member_id),
        )
    )

    assert {event.id for event in result} == {public_event.id, own_private_event.id}


async def test_update_allows_organizer_before_registration():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[member_id], status=EventStatus.CREATED)
    service, _event_repo, _organizer_repo, _time_repo = make_service([event])

    result = await service.update(
        UpdateEventCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, member_id=member_id),
            name="Updated Event",
            team_size=3,
        )
    )

    assert result.name == "Updated Event"
    assert result.team_size == 3


async def test_update_rejects_after_registration_opened():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[member_id], status=EventStatus.REGISTRATION)
    service, _event_repo, _organizer_repo, _time_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.update(
            UpdateEventCommand(
                event_id=event.id,
                access_data=make_access(server_id=server_id, member_id=member_id),
                name="Too Late",
            )
        )


async def test_complete_rejects_active_matches():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(
        server_id=server_id,
        organizer_member_ids=[member_id],
        status=EventStatus.IN_PROGRESS,
        match_type=EventMatchType.SINGLE,
    )
    service, _event_repo, _organizer_repo, _time_repo = make_service([event], incomplete_count=1)

    with pytest.raises(ConflictException):
        await service.complete(
            CompleteEventCommand(
                event_id=event.id,
                access_data=make_access(server_id=server_id, member_id=member_id),
            )
        )


async def test_complete_transitions_single_event_without_active_matches():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(
        server_id=server_id,
        organizer_member_ids=[member_id],
        status=EventStatus.IN_PROGRESS,
        match_type=EventMatchType.SINGLE,
    )
    service, _event_repo, _organizer_repo, _time_repo = make_service([event], incomplete_count=0)

    result = await service.complete(
        CompleteEventCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, member_id=member_id),
        )
    )

    assert result.status == EventStatus.COMPLETED


async def test_cancel_allows_organizer():
    server_id = uuid4()
    member_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[member_id], status=EventStatus.REGISTRATION)
    service, _event_repo, _organizer_repo, _time_repo = make_service([event])

    result = await service.cancel(
        CancelEventCommand(event_id=event.id, access_data=make_access(server_id=server_id, member_id=member_id))
    )

    assert result.status == EventStatus.CANCELLED
