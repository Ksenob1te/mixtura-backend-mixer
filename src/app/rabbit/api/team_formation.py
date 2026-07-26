from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.team import TeamDetail
from src.app.rabbit.models.team_formation import (
    ChooseTeamFormationVariantMessage,
    GetTeamFormationMessage,
    RunTeamFormationMessage,
    TeamFormationJob,
)
from src.core.commands.team_formation import (
    ChooseTeamFormationVariantCommand,
    GetTeamFormationCommand,
    RunTeamFormationCommand,
)
from src.core.response import ResponseMessage
from src.dependency import TeamFormationServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.team_formation.run")
async def run_team_formation(
    data: RunTeamFormationMessage,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[TeamFormationJob]:
    command = RunTeamFormationCommand(**data.model_dump())
    result = await service.run(command)
    return ResponseMessage(status=200, message=TeamFormationJob(**result.model_dump()))


@router.subscriber(queue="event.team_formation.get")
async def get_team_formation(
    data: GetTeamFormationMessage,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[TeamFormationJob]:
    command = GetTeamFormationCommand(**data.model_dump())
    result = await service.get(command)
    return ResponseMessage(status=200, message=TeamFormationJob(**result.model_dump()))


@router.subscriber(queue="event.team_formation.choose")
async def choose_team_formation_variant(
    data: ChooseTeamFormationVariantMessage,
    service: TeamFormationServiceDependency,
) -> ResponseMessage[list[TeamDetail]]:
    command = ChooseTeamFormationVariantCommand(**data.model_dump())
    result = await service.choose_variant(command)
    return ResponseMessage(status=200, message=[TeamDetail(**r.model_dump()) for r in result])
