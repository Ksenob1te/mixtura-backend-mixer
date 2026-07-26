from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.organizer import (
    AddOrganizerMessage,
    ListOrganizersMessage,
    OrganizerItem,
    RemoveOrganizerMessage,
)
from src.core.commands.organizer import (
    AddOrganizerCommand,
    ListOrganizersCommand,
    RemoveOrganizerCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.dependency import OrganizerServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.organizer.list")
async def list_organizers(
    data: ListOrganizersMessage,
    service: OrganizerServiceDependency,
) -> ResponseMessage[list[OrganizerItem]]:
    command = ListOrganizersCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[OrganizerItem(**r.model_dump()) for r in result])


@router.subscriber(queue="event.organizer.add")
async def add_organizer(
    data: AddOrganizerMessage,
    service: OrganizerServiceDependency,
) -> ResponseMessage[OrganizerItem]:
    command = AddOrganizerCommand(**data.model_dump())
    result = await service.add(command)
    return ResponseMessage(status=200, message=OrganizerItem(**result.model_dump()))


@router.subscriber(queue="event.organizer.remove")
async def remove_organizer(
    data: RemoveOrganizerMessage,
    service: OrganizerServiceDependency,
) -> ResponseMessage[StatusResponse]:
    command = RemoveOrganizerCommand(**data.model_dump())
    await service.remove(command)
    return ResponseMessage(status=200, message=StatusResponse())
