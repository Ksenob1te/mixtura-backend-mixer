from faststream.rabbit import RabbitRouter

from src.core.commands.event import (
    CreateEventCommand,
    GetEventCommand,
    ListEventsCommand,
    UpdateEventCommand,
    ActivateEventCommand,
    OpenRegistrationCommand,
    CloseRegistrationCommand,
    CancelEventCommand,
    CompleteEventCommand,
)
from src.core.response import ResponseMessage
from src.core.results.event import EventCard, EventDetail
from src.dependency import EventServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.create")
async def create_event(
    data: CreateEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.create(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.get")
async def get_event(
    data: GetEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.list")
async def list_events(
    data: ListEventsCommand,
    service: EventServiceDependency,
) -> ResponseMessage[list[EventCard]]:
    result = await service.list(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.update")
async def update_event(
    data: UpdateEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.update(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.activate")
async def activate_event(
    data: ActivateEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.activate(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.registration.open")
async def open_registration(
    data: OpenRegistrationCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.open_registration(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.registration.close")
async def close_registration(
    data: CloseRegistrationCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.close_registration(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.cancel")
async def cancel_event(
    data: CancelEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.cancel(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.complete")
async def complete_event(
    data: CompleteEventCommand,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetail]:
    result = await service.complete(data)
    return ResponseMessage(status=200, message=result)
