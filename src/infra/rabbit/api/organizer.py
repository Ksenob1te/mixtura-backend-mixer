from faststream.rabbit import RabbitRouter

from src.core.commands.organizer import (
    ListOrganizersCommand,
    AddOrganizerCommand,
    RemoveOrganizerCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.dependency import OrganizerServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.organizer.list")
async def list_organizers(
    data: ListOrganizersCommand,
    service: OrganizerServiceDependency,
) -> ResponseMessage[list[dict]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.organizer.add")
async def add_organizer(
    data: AddOrganizerCommand,
    service: OrganizerServiceDependency,
) -> ResponseMessage[dict]:
    result = await service.add(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.organizer.remove")
async def remove_organizer(
    data: RemoveOrganizerCommand,
    service: OrganizerServiceDependency,
) -> ResponseMessage[StatusResponse]:
    await service.remove(data)
    return ResponseMessage(status=200, message=StatusResponse())
