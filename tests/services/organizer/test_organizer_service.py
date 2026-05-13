from uuid import uuid4

import pytest

from src.core.commands.organizer import AddOrganizerCommand, ListOrganizersCommand, RemoveOrganizerCommand
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_MANAGE_ORGANIZERS
from src.core.models.event import EventStatus
from src.core.services.organizer import OrganizerService
from tests.services.helpers import (
    InMemoryEventRepository,
    InMemoryOrganizerRepository,
    make_access,
    make_event,
)

pytestmark = pytest.mark.asyncio


def make_service(events):
    event_repo = InMemoryEventRepository(events)
    organizer_repo = InMemoryOrganizerRepository(event_repo)
    return OrganizerService(organizer_repo=organizer_repo, event_repo=event_repo), organizer_repo


async def test_get_list_allows_existing_organizer():
    server_id = uuid4()
    owner_id = uuid4()
    event = make_event(server_id=server_id, is_public=False, organizer_member_ids=[owner_id])
    service, _organizer_repo = make_service([event])

    result = await service.get_list(
        ListOrganizersCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, member_id=owner_id),
        )
    )

    assert len(result) == 1
    assert result[0].member_id == owner_id


async def test_get_list_hides_private_event_from_non_viewer():
    server_id = uuid4()
    event = make_event(server_id=server_id, is_public=False, organizer_member_ids=[uuid4()])
    service, _organizer_repo = make_service([event])

    with pytest.raises(NotFoundException):
        await service.get_list(
            ListOrganizersCommand(event_id=event.id, access_data=make_access(server_id=server_id))
        )


async def test_get_list_rejects_public_event_non_viewer_without_admin_view():
    server_id = uuid4()
    event = make_event(server_id=server_id, is_public=True, organizer_member_ids=[uuid4()])
    service, _organizer_repo = make_service([event])

    with pytest.raises(ForbiddenException):
        await service.get_list(
            ListOrganizersCommand(event_id=event.id, access_data=make_access(server_id=server_id))
        )


async def test_add_organizer_allows_existing_organizer():
    server_id = uuid4()
    owner_id = uuid4()
    new_member_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[owner_id])
    service, organizer_repo = make_service([event])

    result = await service.add(
        AddOrganizerCommand(
            event_id=event.id,
            member_id=new_member_id,
            access_data=make_access(server_id=server_id, member_id=owner_id),
        )
    )

    organizers = await organizer_repo.list_by_event(event.id)
    assert result.member_id == new_member_id
    assert {organizer.member_id for organizer in organizers} == {owner_id, new_member_id}


async def test_add_organizer_allows_event_admin_permission():
    server_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[uuid4()])
    service, _organizer_repo = make_service([event])

    result = await service.add(
        AddOrganizerCommand(
            event_id=event.id,
            member_id=uuid4(),
            access_data=make_access(
                server_id=server_id,
                permission_mask=P_EVENT_ADMIN_MANAGE_ORGANIZERS,
            ),
        )
    )

    assert result.event_id == event.id


async def test_add_organizer_rejects_duplicate_member():
    server_id = uuid4()
    owner_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[owner_id])
    service, _organizer_repo = make_service([event])

    with pytest.raises(ConflictException):
        await service.add(
            AddOrganizerCommand(
                event_id=event.id,
                member_id=owner_id,
                access_data=make_access(server_id=server_id, member_id=owner_id),
            )
        )


async def test_add_organizer_rejects_completed_event():
    server_id = uuid4()
    owner_id = uuid4()
    event = make_event(
        server_id=server_id,
        organizer_member_ids=[owner_id],
        status=EventStatus.COMPLETED,
    )
    service, _organizer_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.add(
            AddOrganizerCommand(
                event_id=event.id,
                member_id=uuid4(),
                access_data=make_access(server_id=server_id, member_id=owner_id),
            )
        )


async def test_remove_organizer_rejects_last_organizer():
    server_id = uuid4()
    owner_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[owner_id])
    service, _organizer_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.remove(
            RemoveOrganizerCommand(
                event_id=event.id,
                member_id=owner_id,
                access_data=make_access(server_id=server_id, member_id=owner_id),
            )
        )


async def test_remove_organizer_deletes_target_when_multiple_exist():
    server_id = uuid4()
    owner_id = uuid4()
    target_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[owner_id, target_id])
    service, organizer_repo = make_service([event])

    await service.remove(
        RemoveOrganizerCommand(
            event_id=event.id,
            member_id=target_id,
            access_data=make_access(server_id=server_id, member_id=owner_id),
        )
    )

    organizers = await organizer_repo.list_by_event(event.id)
    assert [organizer.member_id for organizer in organizers] == [owner_id]
