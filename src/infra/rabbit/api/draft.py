from faststream.rabbit import RabbitRouter

from src.core.commands.draft import CreateDraftCommand, GetDraftCommand, ListDraftsCommand
from src.core.response import ResponseMessage
from src.core.usecases.draft import CreateDraftUseCase, GetDraftUseCase, ListDraftsUseCase
from src.dependency import (
    CreateDraftUseCaseDependency,
    GetDraftUseCaseDependency,
    ListDraftsUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.draft.create")
async def create_draft(
    data: CreateDraftCommand,
    use_case: CreateDraftUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.get")
async def get_draft(
    data: GetDraftCommand,
    use_case: GetDraftUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.draft.list")
async def list_drafts(
    data: ListDraftsCommand,
    use_case: ListDraftsUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
