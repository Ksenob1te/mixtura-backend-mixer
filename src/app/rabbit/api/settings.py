from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.event import (
    ApplicationFormSettingsResponse,
    EventDetailResponse,
)
from src.app.rabbit.models.settings import (
    AddCustomFieldMessage,
    AddGameRoleMessage,
    AddIntegrationMessage,
    GetApplicationFormSettingsMessage,
    RemoveCustomFieldMessage,
    RemoveGameRoleMessage,
    RemoveIntegrationMessage,
    UpdateCustomFieldMessage,
    UpdateGameRoleMessage,
    UpdateTimeSettingsMessage,
)
from src.core.commands.settings import (
    AddCustomFieldCommand,
    AddGameRoleCommand,
    AddIntegrationCommand,
    GetApplicationFormSettingsCommand,
    RemoveCustomFieldCommand,
    RemoveGameRoleCommand,
    RemoveIntegrationCommand,
    UpdateCustomFieldCommand,
    UpdateGameRoleCommand,
    UpdateTimeSettingsCommand,
)
from src.core.response import ResponseMessage
from src.dependency import SettingsServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.settings.integration.add")
async def add_integration(
    data: AddIntegrationMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = AddIntegrationCommand(**data.model_dump())
    result = await service.add_integration(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.integration.remove")
async def remove_integration(
    data: RemoveIntegrationMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = RemoveIntegrationCommand(**data.model_dump())
    result = await service.remove_integration(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.roles.add")
async def add_game_role(
    data: AddGameRoleMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = AddGameRoleCommand(**data.model_dump())
    result = await service.add_game_role(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.roles.update")
async def update_game_role(
    data: UpdateGameRoleMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = UpdateGameRoleCommand(**data.model_dump())
    result = await service.update_game_role(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.roles.remove")
async def remove_game_role(
    data: RemoveGameRoleMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = RemoveGameRoleCommand(**data.model_dump())
    result = await service.remove_game_role(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.custom_fields.add")
async def add_custom_field(
    data: AddCustomFieldMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = AddCustomFieldCommand(**data.model_dump())
    result = await service.add_custom_field(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.custom_fields.update")
async def update_custom_field(
    data: UpdateCustomFieldMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = UpdateCustomFieldCommand(**data.model_dump())
    result = await service.update_custom_field(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.custom_fields.remove")
async def remove_custom_field(
    data: RemoveCustomFieldMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = RemoveCustomFieldCommand(**data.model_dump())
    result = await service.remove_custom_field(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.settings.time_settings.update")
async def update_time_settings(
    data: UpdateTimeSettingsMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = UpdateTimeSettingsCommand(**data.model_dump())
    result = await service.update_time_settings(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.application.form_settings")
async def get_application_form_settings(
    data: GetApplicationFormSettingsMessage,
    service: SettingsServiceDependency,
) -> ResponseMessage[ApplicationFormSettingsResponse]:
    command = GetApplicationFormSettingsCommand(**data.model_dump())
    result = await service.get_application_form_settings(command)
    return ResponseMessage(status=200, message=ApplicationFormSettingsResponse(**result.model_dump()))
