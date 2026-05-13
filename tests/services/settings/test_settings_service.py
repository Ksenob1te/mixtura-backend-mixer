from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.core.commands.settings import (
    AddCustomFieldCommand,
    AddGameRoleCommand,
    AddIntegrationCommand,
    GetApplicationFormSettingsCommand,
    RemoveCustomFieldCommand,
    RemoveGameRoleCommand,
    UpdateCustomFieldCommand,
    UpdateGameRoleCommand,
    UpdateTimeSettingsCommand,
)
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException
from src.core.models.event import EventStatus
from src.core.services.settings import SettingsService
from tests.services.helpers import (
    InMemoryApplicationCustomFieldRepository,
    InMemoryEventRepository,
    InMemoryRequiredIntegrationRepository,
    InMemorySelectedGameRoleRepository,
    InMemoryTimeSettingsRepository,
    make_access,
    make_custom_field,
    make_event,
    make_required_integration,
    make_selected_game_role,
    make_time_settings,
)

pytestmark = pytest.mark.asyncio


def make_service(events):
    event_repo = InMemoryEventRepository(events)
    integration_repo = InMemoryRequiredIntegrationRepository(event_repo)
    role_repo = InMemorySelectedGameRoleRepository(event_repo)
    field_repo = InMemoryApplicationCustomFieldRepository(event_repo)
    time_repo = InMemoryTimeSettingsRepository(event_repo)
    service = SettingsService(
        event_repo=event_repo,
        integration_repo=integration_repo,
        role_repo=role_repo,
        field_repo=field_repo,
        time_repo=time_repo,
    )
    return service, integration_repo, role_repo, field_repo, time_repo


async def test_add_integration_by_organizer_updates_event_detail():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], status=EventStatus.CREATED)
    service, integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    result = await service.add_integration(
        AddIntegrationCommand(
            event_id=event.id,
            name="discord",
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    integrations = await integration_repo.list_by_event(event.id)
    assert [integration.name for integration in result.required_integrations] == ["discord"]
    assert [integration.name for integration in integrations] == ["discord"]


async def test_add_integration_rejects_duplicate_name_case_insensitive():
    server_id = uuid4()
    organizer_id = uuid4()
    existing = make_required_integration(uuid4(), name="Discord")
    event = make_event(
        id=existing.event_id,
        server_id=server_id,
        organizer_member_ids=[organizer_id],
        required_integrations=[existing],
    )
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(ConflictException):
        await service.add_integration(
            AddIntegrationCommand(
                event_id=event.id,
                name="discord",
                access_data=make_access(server_id=server_id, member_id=organizer_id),
            )
        )


async def test_add_integration_rejects_non_organizer_without_admin_permission():
    server_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[uuid4()])
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(ForbiddenException):
        await service.add_integration(
            AddIntegrationCommand(
                event_id=event.id,
                name="discord",
                access_data=make_access(server_id=server_id),
            )
        )


async def test_add_update_remove_game_role_flow():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id])
    service, _integration_repo, role_repo, _field_repo, _time_repo = make_service([event])
    game_role_id = uuid4()

    added = await service.add_game_role(
        AddGameRoleCommand(
            event_id=event.id,
            game_role_id=game_role_id,
            override_min_count=1,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )
    selected_role_id = added.selected_game_roles[0].id

    updated = await service.update_game_role(
        UpdateGameRoleCommand(
            event_id=event.id,
            selected_role_id=selected_role_id,
            override_min_count=2,
            override_max_count=3,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )
    await service.remove_game_role(
        RemoveGameRoleCommand(
            event_id=event.id,
            selected_role_id=selected_role_id,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    assert added.selected_game_roles[0].game_role_id == game_role_id
    assert updated.selected_game_roles[0].override_min_count == 2
    assert updated.selected_game_roles[0].override_max_count == 3
    assert await role_repo.list_by_event(event.id) == []


async def test_add_game_role_rejects_after_registration_opened():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(
        server_id=server_id,
        organizer_member_ids=[organizer_id],
        status=EventStatus.REGISTRATION,
    )
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.add_game_role(
            AddGameRoleCommand(
                event_id=event.id,
                game_role_id=uuid4(),
                access_data=make_access(server_id=server_id, member_id=organizer_id),
            )
        )


async def test_add_update_remove_custom_field_flow():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], use_application=True)
    service, _integration_repo, _role_repo, field_repo, _time_repo = make_service([event])

    added = await service.add_custom_field(
        AddCustomFieldCommand(
            event_id=event.id,
            name="Rank",
            is_private=True,
            is_required=True,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )
    field_id = added.custom_fields[0].id

    updated = await service.update_custom_field(
        UpdateCustomFieldCommand(
            event_id=event.id,
            field_id=field_id,
            name="Visible rank",
            is_private=False,
            is_required=True,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )
    await service.remove_custom_field(
        RemoveCustomFieldCommand(
            event_id=event.id,
            field_id=field_id,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    assert added.custom_fields[0].is_private is True
    assert updated.custom_fields[0].name == "Visible rank"
    assert await field_repo.list_by_event(event.id) == []


async def test_add_custom_field_requires_application_mode():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], use_application=False)
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.add_custom_field(
            AddCustomFieldCommand(
                event_id=event.id,
                name="Rank",
                access_data=make_access(server_id=server_id, member_id=organizer_id),
            )
        )


async def test_update_time_settings_creates_utc_naive_settings():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], use_application=True)
    service, _integration_repo, _role_repo, _field_repo, time_repo = make_service([event])
    start_time = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    result = await service.update_time_settings(
        UpdateTimeSettingsCommand(
            event_id=event.id,
            start_time=start_time,
            end_time=end_time,
            access_data=make_access(server_id=server_id, member_id=organizer_id),
        )
    )

    settings = await time_repo.get_by_event_id(event.id)
    assert result.time_settings is not None
    assert settings is not None
    assert settings.start_time == datetime(2026, 1, 1, 10, 0)
    assert settings.start_time.tzinfo is None


async def test_update_time_settings_rejects_invalid_range():
    server_id = uuid4()
    organizer_id = uuid4()
    event = make_event(server_id=server_id, organizer_member_ids=[organizer_id], use_application=True)
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.update_time_settings(
            UpdateTimeSettingsCommand(
                event_id=event.id,
                start_time=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
                access_data=make_access(server_id=server_id, member_id=organizer_id),
            )
        )


async def test_get_application_form_settings_hides_private_fields_for_anonymous_member():
    server_id = uuid4()
    public_field = make_custom_field(uuid4(), name="Nickname", is_private=False)
    private_field = make_custom_field(public_field.event_id, name="Phone", is_private=True)
    integration = make_required_integration(public_field.event_id, name="discord")
    role = make_selected_game_role(public_field.event_id)
    settings = make_time_settings(public_field.event_id)
    event = make_event(
        id=public_field.event_id,
        server_id=server_id,
        status=EventStatus.REGISTRATION,
        use_application=True,
        custom_fields=[public_field, private_field],
        required_integrations=[integration],
        selected_game_roles=[role],
        time_settings=settings,
    )
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    result = await service.get_application_form_settings(
        GetApplicationFormSettingsCommand(
            event_id=event.id,
            access_data=make_access(server_id=server_id, anonymous=True),
        )
    )

    assert [field.name for field in result.custom_fields] == ["Nickname"]
    assert [item.name for item in result.required_integrations] == ["discord"]
    assert [item.id for item in result.available_roles] == [role.id]
    assert result.time_settings is not None


async def test_get_application_form_settings_rejects_non_admin_before_registration():
    server_id = uuid4()
    event = make_event(server_id=server_id, status=EventStatus.CREATED, use_application=True)
    service, _integration_repo, _role_repo, _field_repo, _time_repo = make_service([event])

    with pytest.raises(BadRequestException):
        await service.get_application_form_settings(
            GetApplicationFormSettingsCommand(event_id=event.id, access_data=make_access(server_id=server_id))
        )
