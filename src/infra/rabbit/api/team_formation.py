from faststream.rabbit import RabbitRouter

from src.core.commands.team_formation import (
    RunTeamFormationCommand,
    GetTeamFormationCommand,
    ChooseTeamFormationVariantCommand,
)
from src.core.response import ResponseMessage
from src.core.results.team import TeamDetail
from src.core.results.team_formation import TeamFormationJob
from src.dependency import TeamFormationServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.team_formation.run")
async def run_team_formation(
    data: RunTeamFormationCommand,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[TeamFormationJob]:
    result = await service.run(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.team_formation.get")
async def get_team_formation(
    data: GetTeamFormationCommand,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[TeamFormationJob]:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.team_formation.choose")
async def choose_team_formation_variant(
    data: ChooseTeamFormationVariantCommand,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[list[TeamDetail]]:
    result = await service.choose_variant(data)
    return ResponseMessage(status=200, message=result)
