from faststream.rabbit import RabbitRouter

from src.core.commands.match import GetMatchCommand, ListMatchesCommand, RecordMatchResultCommand, SetupMatchCommand
from src.core.response import ResponseMessage
from src.dependency import (
    GetMatchUseCaseDependency,
    ListMatchesUseCaseDependency,
    RecordSingleMatchResultUseCaseDependency,
    SingleMatchSetupUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.match.setup")
async def setup_single_match(
    data: SetupMatchCommand,
    use_case: SingleMatchSetupUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.result.record")
async def record_single_match_result(
    data: RecordMatchResultCommand,
    use_case: RecordSingleMatchResultUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.get")
async def get_match(
    data: GetMatchCommand,
    use_case: GetMatchUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.list")
async def list_matches(
    data: ListMatchesCommand,
    use_case: ListMatchesUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
