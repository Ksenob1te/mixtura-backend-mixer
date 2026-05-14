from uuid import uuid4

import pytest

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.event import (
    ActivateEventCommand,
    CancelEventCommand,
    CloseRegistrationCommand,
    CompleteEventCommand,
    CreateEventCommand,
    GetEventCommand,
    ListEventsCommand,
    OpenRegistrationCommand,
    UpdateEventCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException
from src.core.interfaces.repo.access import P_EVENT_ADMIN_VIEW, P_EVENT_CREATE
from src.core.models.bracket import BracketCreate
from src.core.models.event import EventCreate, EventMatchType, EventStatus, TeamFormation
from src.core.models.match import MatchCreate
from src.core.models.organizer import OrganizerCreate
from src.core.models.stage import StageCreate, StageFormat
from src.core.models.stage_group import StageGroupCreate

pytestmark = pytest.mark.asyncio


def access(server_id, member_id=None, permission_mask=0, restriction_mask=0) -> AccessDataRequest:
    return AccessDataRequest(
        server_id=server_id,
        member_id=member_id,
        permission_mask=permission_mask,
        restriction_mask=restriction_mask,
    )


class TestEventService:
    async def test_create_event_creates_owner_and_time_settings(self, event_service, event_repo, organizer_repo, application_time_settings_repo, server_id, member_id):
        result = await event_service.create(
            CreateEventCommand(
                access_data=access(server_id, member_id, permission_mask=P_EVENT_CREATE),
                name="Spring Mix",
                match_type=EventMatchType.SINGLE,
                use_application=True,
                is_public=True,
                team_size=5,
                team_formation=TeamFormation.BALANCE,
                allow_multiple_drafts=False,
            )
        )

        assert await event_repo.get(result.id) is not None
        assert [item.member_id for item in result.organizers] == [member_id]
        assert result.time_settings is not None
        assert await organizer_repo.list_by_event(result.id)
        assert await application_time_settings_repo.get_by_event_id(result.id) is not None

    async def test_create_requires_event_create_permission(self, event_service, server_id, member_id):
        with pytest.raises(ForbiddenException):
            await event_service.create(
                CreateEventCommand(
                    access_data=access(server_id, member_id),
                    name="NoPermission",
                    match_type=EventMatchType.SINGLE,
                    use_application=True,
                    is_public=True,
                    team_size=5,
                    team_formation=TeamFormation.BALANCE,
                    allow_multiple_drafts=False,
                )
            )

    async def test_get_rejects_different_server(self, event_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))

        with pytest.raises(ForbiddenException):
            await event_service.get(GetEventCommand(event_id=event.id, access_data=access(uuid4())))

    async def test_get_list_hides_private_event_from_non_viewer(self, event_service, event_repo, organizer_repo, server_id, member_id):
        public_event = await event_repo.create(EventCreate(server_id=server_id, name="Public", is_public=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        own_private_event = await event_repo.create(EventCreate(server_id=server_id, name="Own Private", is_public=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await event_repo.create(EventCreate(server_id=server_id, name="Other Private", is_public=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=own_private_event.id, member_id=member_id))

        result = await event_service.get_list(ListEventsCommand(server_id=server_id, access_data=access(server_id, member_id)))
        assert {item.id for item in result} == {public_event.id, own_private_event.id}

    async def test_get_list_allows_admin_view_for_private_event(self, event_service, event_repo, server_id):
        private_event = await event_repo.create(EventCreate(server_id=server_id, name="Private", is_public=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))

        result = await event_service.get_list(ListEventsCommand(server_id=server_id, access_data=access(server_id, permission_mask=P_EVENT_ADMIN_VIEW)))
        assert [item.id for item in result] == [private_event.id]

    async def test_update_allows_organizer_before_registration(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        result = await event_service.update(UpdateEventCommand(event_id=event.id, access_data=access(server_id, member_id), name="Updated Event", team_size=3))
        assert result.name == "Updated Event"
        assert result.team_size == 3

    async def test_update_rejects_non_organizer_without_admin(self, event_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))

        with pytest.raises(ForbiddenException):
            await event_service.update(UpdateEventCommand(event_id=event.id, access_data=access(server_id, uuid4()), name="Denied"))

    async def test_update_rejects_after_registration_opened(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        with pytest.raises(BadRequestException):
            await event_service.update(UpdateEventCommand(event_id=event.id, access_data=access(server_id, member_id), name="Too Late"))

    async def test_activate_open_and_close_registration_flow(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Flow", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        activated = await event_service.activate(ActivateEventCommand(event_id=event.id, access_data=access(server_id, member_id)))
        opened = await event_service.open_registration(OpenRegistrationCommand(event_id=event.id, access_data=access(server_id, member_id)))
        closed = await event_service.close_registration(CloseRegistrationCommand(event_id=event.id, access_data=access(server_id, member_id)))

        assert activated.status == EventStatus.IDLE
        assert opened.status == EventStatus.REGISTRATION
        assert closed.status == EventStatus.IDLE

    async def test_complete_rejects_active_matches(self, event_service, event_repo, organizer_repo, bracket_repo, stage_repo, stage_group_repo, match_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.IN_PROGRESS, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))
        bracket = await bracket_repo.create(BracketCreate(event_id=event.id))
        stage = await stage_repo.create(StageCreate(stage_index=1, bracket_id=bracket.id, format=StageFormat.SINGLE_MATCH, name="Stage"))
        group = await stage_group_repo.create(StageGroupCreate(stage_id=stage.id, name="Group A"))
        await match_repo.create(MatchCreate(group_id=group.id, match_index=1))

        with pytest.raises(ConflictException):
            await event_service.complete(CompleteEventCommand(event_id=event.id, access_data=access(server_id, member_id)))

    async def test_complete_transitions_single_event_without_active_matches(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.IN_PROGRESS, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        result = await event_service.complete(CompleteEventCommand(event_id=event.id, access_data=access(server_id, member_id)))
        assert result.status == EventStatus.COMPLETED

    async def test_complete_rejects_tournament_event(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Tournament", status=EventStatus.IN_PROGRESS, match_type=EventMatchType.TOURNAMENT, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        with pytest.raises(BadRequestException):
            await event_service.complete(CompleteEventCommand(event_id=event.id, access_data=access(server_id, member_id)))

    async def test_cancel_allows_organizer(self, event_service, event_repo, organizer_repo, server_id, member_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=TeamFormation.BALANCE, allow_multiple_drafts=False))
        await organizer_repo.create(OrganizerCreate(event_id=event.id, member_id=member_id))

        result = await event_service.cancel(CancelEventCommand(event_id=event.id, access_data=access(server_id, member_id)))
        assert result.status == EventStatus.CANCELLED
