from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.match import (
    GetMatchMessage,
    ListMatchesMessage,
    RecordMatchResultMessage,
    SetupMatchMessage,
    SingleMatchView,
)
from src.core.commands.match import (
    GetMatchCommand,
    ListMatchesCommand,
    RecordMatchResultCommand,
    SetupMatchCommand,
)
from src.core.response import ResponseMessage
from src.dependency import MatchServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.match.setup")
async def setup_single_match(
    data: SetupMatchMessage,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    command = SetupMatchCommand(**data.model_dump())
    result = await service.setup(command)
    return ResponseMessage(status=200, message=SingleMatchView(**result.model_dump()))


@router.subscriber(queue="event.match.result.record")
async def record_single_match_result(
    data: RecordMatchResultMessage,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    command = RecordMatchResultCommand(**data.model_dump())
    result = await service.record_result(command)
    return ResponseMessage(status=200, message=SingleMatchView(**result.model_dump()))


@router.subscriber(queue="event.match.get")
async def get_match(
    data: GetMatchMessage,
    service: MatchServiceDependency,
) -> ResponseMessage[SingleMatchView]:
    command = GetMatchCommand(**data.model_dump())
    result = await service.get(command)
    return ResponseMessage(status=200, message=SingleMatchView(**result.model_dump()))


@router.subscriber(queue="event.match.list")
async def list_matches(
    data: ListMatchesMessage,
    service: MatchServiceDependency,
) -> ResponseMessage[list[SingleMatchView]]:
    command = ListMatchesCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[SingleMatchView(**r.model_dump()) for r in result])
