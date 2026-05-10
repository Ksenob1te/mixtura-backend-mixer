from faststream.rabbit import RabbitRouter

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.response import ResponseMessage
from src.dependency import DraftServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.draft.create")
async def create_draft(
    data: CreateDraftCommand,
    service: DraftServiceDependency,
) -> ResponseMessage:
    result = await service.create(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.get")
async def get_draft(
    data: GetDraftCommand,
    service: DraftServiceDependency,
) -> ResponseMessage:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.list")
async def list_drafts(
    data: ListDraftsCommand,
    service: DraftServiceDependency,
) -> ResponseMessage:
    result = await service.list(data)
    return ResponseMessage(status=200, message=result)
