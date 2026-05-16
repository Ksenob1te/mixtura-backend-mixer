from faststream.rabbit import RabbitRouter

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.response import ResponseMessage
from src.core.results.draft import DraftDetail, DraftItem
from src.dependency import DraftServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.draft.create")
async def create_draft(
    data: CreateDraftCommand,
    service: DraftServiceDependency,
) -> ResponseMessage[DraftDetail]:
    result = await service.create(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.get")
async def get_draft(
    data: GetDraftCommand,
    service: DraftServiceDependency,
) -> ResponseMessage[DraftDetail]:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.list")
async def list_drafts(
    data: ListDraftsCommand,
    service: DraftServiceDependency,
) -> ResponseMessage[list[DraftItem]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)
