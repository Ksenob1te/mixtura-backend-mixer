from uuid import uuid4

import pytest

from src.core.commands.organizer import AddOrganizerCommand, ListOrganizersCommand, RemoveOrganizerCommand
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_MANAGE_ORGANIZERS
from src.core.models.event import EventCreate, EventMatchType, EventStatus

pytestmark = pytest.mark.asyncio


class TestOrganizerService:
    async def test_get_list_allows_existing_organizer(self, organizer_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        result = await organizer_service.get_list(ListOrganizersCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert len(result) == 1
        assert result[0].member_id == organizer_id

    async def test_get_list_hides_private_event_from_non_viewer(self, organizer_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))

        with pytest.raises(NotFoundException):
            await organizer_service.get_list(ListOrganizersCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id)))

    async def test_get_list_rejects_public_event_non_viewer_without_admin_view(self, organizer_service, event_repo, organizer_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await organizer_service.get_list(ListOrganizersCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id)))

    async def test_add_organizer_rejects_duplicate_member(self, organizer_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(ConflictException):
            await organizer_service.add(AddOrganizerCommand(event_id=event.id, member_id=organizer_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_add_organizer_allows_event_admin_permission(self, organizer_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))

        result = await organizer_service.add(AddOrganizerCommand(event_id=event.id, member_id=uuid4(), access_data=AccessDataRequest(server_id=server_id, permission_mask=P_EVENT_ADMIN_MANAGE_ORGANIZERS)))

        assert result.event_id == event.id

    async def test_add_organizer_rejects_completed_event(self, organizer_service, event_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.COMPLETED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(BadRequestException):
            await organizer_service.add(AddOrganizerCommand(event_id=event.id, member_id=uuid4(), access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_remove_organizer_rejects_last_organizer(self, organizer_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(BadRequestException):
            await organizer_service.remove(RemoveOrganizerCommand(event_id=event.id, member_id=organizer_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_remove_organizer_deletes_target_when_multiple_exist(self, organizer_service, event_repo, organizer_repo, server_id, organizer_id):
        target_id = uuid4()
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        await organizer_repo.create(dict(event_id=event.id, member_id=target_id))

        await organizer_service.remove(RemoveOrganizerCommand(event_id=event.id, member_id=target_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        organizers = await organizer_repo.list_by_event(event.id)
        assert [organizer.member_id for organizer in organizers] == [organizer_id]

    async def test_add_organizer_rejects_different_server(self, organizer_service, event_repo, organizer_repo, organizer_id):
        event_server = uuid4()
        event = await event_repo.create(EventCreate(server_id=event_server, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(ForbiddenException):
            await organizer_service.add(
                AddOrganizerCommand(
                    event_id=event.id,
                    member_id=uuid4(),
                    access_data=AccessDataRequest(server_id=uuid4(), member_id=organizer_id),
                )
            )

    async def test_remove_rejects_missing_target_member(self, organizer_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        await organizer_repo.create(dict(event_id=event.id, member_id=uuid4()))

        with pytest.raises(NotFoundException):
            await organizer_service.remove(
                RemoveOrganizerCommand(
                    event_id=event.id,
                    member_id=uuid4(),
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

