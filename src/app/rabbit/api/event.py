from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.event import (
    ActivateEventMessage,
    CancelEventMessage,
    CloseRegistrationMessage,
    CompleteEventMessage,
    CreateEventMessage,
    EventCardResponse,
    EventDetailResponse,
    GetEventMessage,
    ListEventsMessage,
    OpenRegistrationMessage,
    UpdateEventMessage,
)
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
from src.core.response import ResponseMessage
from src.dependency import EventServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.create")
async def create_event(
    data: CreateEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = CreateEventCommand(**data.model_dump())
    result = await service.create(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.get")
async def get_event(
    data: GetEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = GetEventCommand(**data.model_dump())
    result = await service.get(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.list")
async def list_events(
    data: ListEventsMessage,
    service: EventServiceDependency,
) -> ResponseMessage[list[EventCardResponse]]:
    command = ListEventsCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[EventCardResponse(**r.model_dump()) for r in result])


@router.subscriber(queue="event.update")
async def update_event(
    data: UpdateEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = UpdateEventCommand(**data.model_dump())
    result = await service.update(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.activate")
async def activate_event(
    data: ActivateEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = ActivateEventCommand(**data.model_dump())
    result = await service.activate(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.registration.open")
async def open_registration(
    data: OpenRegistrationMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = OpenRegistrationCommand(**data.model_dump())
    result = await service.open_registration(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.registration.close")
async def close_registration(
    data: CloseRegistrationMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = CloseRegistrationCommand(**data.model_dump())
    result = await service.close_registration(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.cancel")
async def cancel_event(
    data: CancelEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = CancelEventCommand(**data.model_dump())
    result = await service.cancel(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.complete")
async def complete_event(
    data: CompleteEventMessage,
    service: EventServiceDependency,
) -> ResponseMessage[EventDetailResponse]:
    command = CompleteEventCommand(**data.model_dump())
    result = await service.complete(command)
    return ResponseMessage(status=200, message=EventDetailResponse(**result.model_dump()))
