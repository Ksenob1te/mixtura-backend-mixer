from faststream.rabbit import RabbitRouter

from src.core.commands.settings import (
    AddIntegrationCommand,
    RemoveIntegrationCommand,
    AddGameRoleCommand,
    UpdateGameRoleCommand,
    RemoveGameRoleCommand,
    AddCustomFieldCommand,
    UpdateCustomFieldCommand,
    RemoveCustomFieldCommand,
    UpdateTimeSettingsCommand,
    GetApplicationFormSettingsCommand,
)
from src.core.response import ResponseMessage
from src.core.results.event import EventDetail, ApplicationFormSettingsResponse
from src.dependency import SettingsServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.settings.integration.add")
async def add_integration(
    data: AddIntegrationCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.add_integration(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.integration.remove")
async def remove_integration(
    data: RemoveIntegrationCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.remove_integration(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.add")
async def add_game_role(
    data: AddGameRoleCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.add_game_role(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.update")
async def update_game_role(
    data: UpdateGameRoleCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.update_game_role(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.remove")
async def remove_game_role(
    data: RemoveGameRoleCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.remove_game_role(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.add")
async def add_custom_field(
    data: AddCustomFieldCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.add_custom_field(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.update")
async def update_custom_field(
    data: UpdateCustomFieldCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.update_custom_field(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.remove")
async def remove_custom_field(
    data: RemoveCustomFieldCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.remove_custom_field(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.time_settings.update")
async def update_time_settings(
    data: UpdateTimeSettingsCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.update_time_settings(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.form_settings")
async def get_application_form_settings(
    data: GetApplicationFormSettingsCommand,
    service: SettingsServiceDependency,
) -> ResponseMessage[ApplicationFormSettingsResponse]:
    result = await service.get_application_form_settings(data)
    return ResponseMessage(status=200, message=result)
