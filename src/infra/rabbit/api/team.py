from faststream.rabbit import RabbitRouter

from src.core.commands.team import ListTeamsCommand
from src.core.response import ResponseMessage
from src.dependency import TeamServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.team.list")
async def list_teams(
    data: ListTeamsCommand,
    service: TeamServiceDependency,
) -> ResponseMessage:
    result = await service.list(data)
    return ResponseMessage(status=200, message=result)
