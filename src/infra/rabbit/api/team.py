from faststream.rabbit import RabbitRouter

from src.core.commands.team import ListTeamsCommand
from src.core.response import ResponseMessage
from src.core.usecases.team import ListTeamsUseCase
from src.dependency import ListTeamsUseCaseDependency

router = RabbitRouter()


@router.subscriber(queue="event.team.list")
async def list_teams(
    data: ListTeamsCommand,
    use_case: ListTeamsUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
