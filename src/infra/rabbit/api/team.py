from faststream.rabbit import RabbitRouter

from src.core.commands.team import ListTeamsCommand
from src.core.response import ResponseMessage
from src.core.results.team import TeamItem
from src.dependency import TeamServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.team.list")
async def list_teams(
    data: ListTeamsCommand,
    service: TeamServiceDependency,
) -> ResponseMessage[list[TeamItem]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)
