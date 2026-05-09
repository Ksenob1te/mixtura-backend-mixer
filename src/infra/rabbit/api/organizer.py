from faststream.rabbit import RabbitRouter

from src.core.commands.organizer import (
    ListOrganizersCommand,
    AddOrganizerCommand,
    RemoveOrganizerCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.core.usecases.organizer import (
    ListOrganizersUseCase,
    AddOrganizerUseCase,
    RemoveOrganizerUseCase,
)
from src.dependency import (
    ListOrganizersUseCaseDependency,
    AddOrganizerUseCaseDependency,
    RemoveOrganizerUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.organizer.list")
async def list_organizers(
    data: ListOrganizersCommand,
    use_case: ListOrganizersUseCaseDependency,
) -> ResponseMessage[list[dict]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.organizer.add")
async def add_organizer(
    data: AddOrganizerCommand,
    use_case: AddOrganizerUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.organizer.remove")
async def remove_organizer(
    data: RemoveOrganizerCommand,
    use_case: RemoveOrganizerUseCaseDependency,
) -> ResponseMessage[StatusResponse]:
    await use_case(data)
    return ResponseMessage(status=200, message=StatusResponse())
