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
    ListEventsCommand,
    GetApplicationFormSettingsCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.core.results.event import EventCard, EventDetail
from src.core.usecases.settings import (
    AddIntegrationUseCase,
    RemoveIntegrationUseCase,
    AddGameRoleUseCase,
    UpdateGameRoleUseCase,
    RemoveGameRoleUseCase,
    AddCustomFieldUseCase,
    UpdateCustomFieldUseCase,
    RemoveCustomFieldUseCase,
    UpdateTimeSettingsUseCase,
    ListEventsUseCase,
    GetApplicationFormSettingsUseCase,
)
from src.dependency import (
    AddIntegrationUseCaseDependency,
    RemoveIntegrationUseCaseDependency,
    AddGameRoleUseCaseDependency,
    UpdateGameRoleUseCaseDependency,
    RemoveGameRoleUseCaseDependency,
    AddCustomFieldUseCaseDependency,
    UpdateCustomFieldUseCaseDependency,
    RemoveCustomFieldUseCaseDependency,
    UpdateTimeSettingsUseCaseDependency,
    ListEventsUseCaseDependency,
    GetApplicationFormSettingsUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.settings.integration.add")
async def add_integration(
    data: AddIntegrationCommand,
    use_case: AddIntegrationUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.integration.remove")
async def remove_integration(
    data: RemoveIntegrationCommand,
    use_case: RemoveIntegrationUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.add")
async def add_game_role(
    data: AddGameRoleCommand,
    use_case: AddGameRoleUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.update")
async def update_game_role(
    data: UpdateGameRoleCommand,
    use_case: UpdateGameRoleUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.roles.remove")
async def remove_game_role(
    data: RemoveGameRoleCommand,
    use_case: RemoveGameRoleUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.add")
async def add_custom_field(
    data: AddCustomFieldCommand,
    use_case: AddCustomFieldUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.update")
async def update_custom_field(
    data: UpdateCustomFieldCommand,
    use_case: UpdateCustomFieldUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.custom_fields.remove")
async def remove_custom_field(
    data: RemoveCustomFieldCommand,
    use_case: RemoveCustomFieldUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.settings.time_settings.update")
async def update_time_settings(
    data: UpdateTimeSettingsCommand,
    use_case: UpdateTimeSettingsUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.list")
async def list_events(
    data: ListEventsCommand,
    use_case: ListEventsUseCaseDependency,
) -> ResponseMessage[list[EventCard]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.form_settings")
async def get_application_form_settings(
    data: GetApplicationFormSettingsCommand,
    use_case: GetApplicationFormSettingsUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data.event_id, data.access_data)
    return ResponseMessage(status=200, message=result)
