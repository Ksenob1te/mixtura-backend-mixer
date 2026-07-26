from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.team import ListTeamsMessage, TeamItem
from src.core.commands.team import ListTeamsCommand
from src.core.response import ResponseMessage
from src.dependency import TeamServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.team.list")
async def list_teams(
    data: ListTeamsMessage,
    service: TeamServiceDependency,
) -> ResponseMessage[list[TeamItem]]:
    command = ListTeamsCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[TeamItem(**r.model_dump()) for r in result])
