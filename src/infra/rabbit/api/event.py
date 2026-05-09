from faststream.rabbit import RabbitRouter

from src.core.commands.event import (
    CreateEventCommand,
    GetEventCommand,
    ListPublicEventsCommand,
    ListPrivateEventsCommand,
    UpdateEventCommand,
    ActivateEventCommand,
    OpenRegistrationCommand,
    CloseRegistrationCommand,
    CancelEventCommand,
    CompleteEventCommand,
)
from src.core.response import ResponseMessage
from src.core.results.event import EventCard, EventDetail
from src.core.usecases.event import (
    CreateEventUseCase,
    GetEventUseCase,
    ListPublicEventsUseCase,
    ListPrivateEventsUseCase,
    UpdateEventUseCase,
    ActivateEventUseCase,
    OpenRegistrationUseCase,
    CloseRegistrationUseCase,
    CancelEventUseCase,
    CompleteSingleGameEventUseCase,
)
from src.dependency import (
    CreateEventUseCaseDependency,
    GetEventUseCaseDependency,
    ListPublicEventsUseCaseDependency,
    ListPrivateEventsUseCaseDependency,
    UpdateEventUseCaseDependency,
    ActivateEventUseCaseDependency,
    OpenRegistrationUseCaseDependency,
    CloseRegistrationUseCaseDependency,
    CancelEventUseCaseDependency,
    CompleteSingleGameEventUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.create")
async def create_event(
    data: CreateEventCommand,
    use_case: CreateEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.get")
async def get_event(
    data: GetEventCommand,
    use_case: GetEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.list_public")
async def list_public_events(
    data: ListPublicEventsCommand,
    use_case: ListPublicEventsUseCaseDependency,
) -> ResponseMessage[list[EventCard]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.list_private")
async def list_private_events(
    data: ListPrivateEventsCommand,
    use_case: ListPrivateEventsUseCaseDependency,
) -> ResponseMessage[list[EventCard]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.update")
async def update_event(
    data: UpdateEventCommand,
    use_case: UpdateEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.activate")
async def activate_event(
    data: ActivateEventCommand,
    use_case: ActivateEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.registration.open")
async def open_registration(
    data: OpenRegistrationCommand,
    use_case: OpenRegistrationUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.registration.close")
async def close_registration(
    data: CloseRegistrationCommand,
    use_case: CloseRegistrationUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.cancel")
async def cancel_event(
    data: CancelEventCommand,
    use_case: CancelEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.complete")
async def complete_event(
    data: CompleteEventCommand,
    use_case: CompleteSingleGameEventUseCaseDependency,
) -> ResponseMessage[EventDetail]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
