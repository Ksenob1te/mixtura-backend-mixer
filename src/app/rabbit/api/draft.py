from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.draft import (
    CreateDraftMessage,
    DraftDetailResponse,
    DraftItem,
    GetDraftMessage,
    ListDraftsMessage,
)
from src.core.commands.draft import (
    CreateDraftCommand,
    GetDraftCommand,
    ListDraftsCommand,
)
from src.core.response import ResponseMessage
from src.dependency import DraftServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.draft.create")
async def create_draft(
    data: CreateDraftMessage,
    service: DraftServiceDependency,
) -> ResponseMessage[DraftDetailResponse]:
    command = CreateDraftCommand(**data.model_dump())
    result = await service.create(command)
    return ResponseMessage(status=200, message=DraftDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.draft.get")
async def get_draft(
    data: GetDraftMessage,
    service: DraftServiceDependency,
) -> ResponseMessage[DraftDetailResponse]:
    command = GetDraftCommand(**data.model_dump())
    result = await service.get(command)
    return ResponseMessage(status=200, message=DraftDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.draft.list")
async def list_drafts(
    data: ListDraftsMessage,
    service: DraftServiceDependency,
) -> ResponseMessage[list[DraftItem]]:
    command = ListDraftsCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[DraftItem(**r.model_dump()) for r in result])
