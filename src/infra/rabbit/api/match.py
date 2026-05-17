from faststream.rabbit import RabbitRouter

from src.core.commands.match import GetMatchCommand, ListMatchesCommand, RecordMatchResultCommand, SetupMatchCommand
from src.core.response import ResponseMessage
from src.core.results.match import SingleMatchView
from src.dependency import MatchServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.match.setup")
async def setup_single_match(
    data: SetupMatchCommand,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    result = await service.setup(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.result.record")
async def record_single_match_result(
    data: RecordMatchResultCommand,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    result = await service.record_result(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.get")
async def get_match(
    data: GetMatchCommand,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.match.list")
async def list_matches(
    data: ListMatchesCommand,
    service: MatchServiceDependency,
) -> ResponseMessage[list[SingleMatchView]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)
