from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.core.commands.settings import (
    AddCustomFieldCommand,
    AddGameRoleCommand,
    AddIntegrationCommand,
    GetApplicationFormSettingsCommand,
    RemoveIntegrationCommand,
    RemoveCustomFieldCommand,
    RemoveGameRoleCommand,
    UpdateCustomFieldCommand,
    UpdateGameRoleCommand,
    UpdateTimeSettingsCommand,
)
from src.core.commands.access_data import AccessDataRequest
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.models.event import EventCreate, EventMatchType, EventStatus
from src.core.models.application_custom_field import ApplicationCustomFieldCreate
from src.core.models.required_integration import RequiredIntegrationCreate
from src.core.models.selected_game_role import SelectedGameRoleCreate
from src.core.models.application_time_settings import ApplicationTimeSettingsCreate

pytestmark = pytest.mark.asyncio


class TestSettingsService:
    async def test_add_integration_by_organizer_updates_event_detail(self, settings_service, event_repo, organizer_repo, required_integration_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        provider_id = uuid4()
        result = await settings_service.add_integration(AddIntegrationCommand(event_id=event.id, provider_id=provider_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        integrations = await required_integration_repo.list_by_event(event.id)
        assert [integration.provider_id for integration in result.required_integrations] == [provider_id]
        assert [integration.provider_id for integration in integrations] == [provider_id]

    async def test_add_integration_rejects_duplicate_provider(self, settings_service, event_repo, required_integration_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        provider_id = uuid4()
        await required_integration_repo.create(RequiredIntegrationCreate(event_id=event.id, provider_id=provider_id))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(ConflictException):
            await settings_service.add_integration(AddIntegrationCommand(event_id=event.id, provider_id=provider_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_add_integration_rejects_non_organizer_without_admin_permission(self, settings_service, event_repo, organizer_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=uuid4()))

        with pytest.raises(ForbiddenException):
            await settings_service.add_integration(AddIntegrationCommand(event_id=event.id, provider_id=uuid4(), access_data=AccessDataRequest(server_id=server_id)))

    async def test_add_update_remove_game_role_flow(self, settings_service, event_repo, selected_game_role_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        game_role_id = uuid4()

        added = await settings_service.add_game_role(AddGameRoleCommand(event_id=event.id, game_role_id=game_role_id, override_min_count=1, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        selected_role_id = added.selected_game_roles[0].id

        updated = await settings_service.update_game_role(UpdateGameRoleCommand(event_id=event.id, selected_role_id=selected_role_id, override_min_count=2, override_max_count=3, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        await settings_service.remove_game_role(RemoveGameRoleCommand(event_id=event.id, selected_role_id=selected_role_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert added.selected_game_roles[0].game_role_id == game_role_id
        assert updated.selected_game_roles[0].override_min_count == 2
        assert updated.selected_game_roles[0].override_max_count == 3
        assert await selected_game_role_repo.list_by_event(event.id) == []

    async def test_add_game_role_rejects_after_registration_opened(self, settings_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, match_type=EventMatchType.SINGLE, use_application=True, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(BadRequestException):
            await settings_service.add_game_role(AddGameRoleCommand(event_id=event.id, game_role_id=uuid4(), access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_add_update_remove_custom_field_flow(self, settings_service, event_repo, application_custom_field_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", use_application=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        added = await settings_service.add_custom_field(AddCustomFieldCommand(event_id=event.id, name="Rank", is_private=True, is_required=True, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        field_id = added.custom_fields[0].id

        updated = await settings_service.update_custom_field(UpdateCustomFieldCommand(event_id=event.id, field_id=field_id, name="Visible rank", is_private=False, is_required=True, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))
        await settings_service.remove_custom_field(RemoveCustomFieldCommand(event_id=event.id, field_id=field_id, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        assert added.custom_fields[0].is_private is True
        assert updated.custom_fields[0].name == "Visible rank"
        assert await application_custom_field_repo.list_by_event(event.id) == []

    async def test_add_custom_field_requires_application_mode(self, settings_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", use_application=False, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(BadRequestException):
            await settings_service.add_custom_field(AddCustomFieldCommand(event_id=event.id, name="Rank", access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_update_time_settings_creates_utc_naive_settings(self, settings_service, event_repo, application_time_settings_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", use_application=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))
        start_time = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

        result = await settings_service.update_time_settings(UpdateTimeSettingsCommand(event_id=event.id, start_time=start_time, end_time=end_time, access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

        settings = await application_time_settings_repo.get_by_event_id(event.id)
        assert result.time_settings is not None
        assert settings is not None
        assert settings.start_time == datetime(2026, 1, 1, 10, 0)
        assert settings.start_time.tzinfo is None

    async def test_update_time_settings_rejects_invalid_range(self, settings_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", use_application=True, status=EventStatus.CREATED, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(BadRequestException):
            await settings_service.update_time_settings(UpdateTimeSettingsCommand(event_id=event.id, start_time=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc), end_time=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc), access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id)))

    async def test_get_application_form_settings_hides_private_fields_for_anonymous_member(self, settings_service, event_repo, application_custom_field_repo, required_integration_repo, selected_game_role_repo, application_time_settings_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.REGISTRATION, use_application=True, is_public=True, match_type=EventMatchType.SINGLE, team_size=5, team_formation=0, allow_multiple_drafts=False))
        public_field = await application_custom_field_repo.create(ApplicationCustomFieldCreate(event_id=event.id, name="Nickname", is_private=False, is_required=False))
        private_field = await application_custom_field_repo.create(ApplicationCustomFieldCreate(event_id=event.id, name="Phone", is_private=True, is_required=False))
        await required_integration_repo.create(RequiredIntegrationCreate(event_id=event.id, provider_id=uuid4()))
        role = await selected_game_role_repo.create(SelectedGameRoleCreate(event_id=event.id, game_role_id=uuid4()))
        await application_time_settings_repo.create(ApplicationTimeSettingsCreate(event_id=event.id, start_time=None, end_time=None))

        result = await settings_service.get_application_form_settings(GetApplicationFormSettingsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id, anonymous=True)))

        assert [field.name for field in result.custom_fields] == ["Nickname"]
        assert len(result.required_integrations) == 1
        assert [item.id for item in result.available_roles] == [role.id]
        assert result.time_settings is not None

    async def test_get_application_form_settings_rejects_non_admin_before_registration(self, settings_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, use_application=True, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))

        with pytest.raises(BadRequestException):
            await settings_service.get_application_form_settings(GetApplicationFormSettingsCommand(event_id=event.id, access_data=AccessDataRequest(server_id=server_id)))

    async def test_remove_integration_rejects_not_found(self, settings_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, use_application=True, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(NotFoundException):
            await settings_service.remove_integration(
                RemoveIntegrationCommand(
                    event_id=event.id,
                    integration_id=uuid4(),
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_update_game_role_rejects_missing_selected_role(self, settings_service, event_repo, organizer_repo, server_id, organizer_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="Event", status=EventStatus.CREATED, use_application=True, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))
        await organizer_repo.create(dict(event_id=event.id, member_id=organizer_id))

        with pytest.raises(NotFoundException):
            await settings_service.update_game_role(
                UpdateGameRoleCommand(
                    event_id=event.id,
                    selected_role_id=uuid4(),
                    override_min_count=1,
                    access_data=AccessDataRequest(server_id=server_id, member_id=organizer_id),
                )
            )

    async def test_get_application_form_settings_rejects_non_application_event(self, settings_service, event_repo, server_id):
        event = await event_repo.create(EventCreate(server_id=server_id, name="NoApp", status=EventStatus.REGISTRATION, use_application=False, match_type=EventMatchType.SINGLE, is_public=True, team_size=5, team_formation=0, allow_multiple_drafts=False))

        with pytest.raises(BadRequestException):
            await settings_service.get_application_form_settings(
                GetApplicationFormSettingsCommand(
                    event_id=event.id,
                    access_data=AccessDataRequest(server_id=server_id, anonymous=True),
                )
            )

