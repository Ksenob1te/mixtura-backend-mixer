from faststream.rabbit import RabbitRouter

from src.core.commands.team_formation import (
    RunTeamFormationCommand,
    GetTeamFormationCommand,
    ChooseTeamFormationVariantCommand,
)
from src.core.response import ResponseMessage
from src.core.usecases.team_formation import (
    RunTeamFormationUseCase,
    GetTeamFormationUseCase,
    ChooseTeamFormationVariantUseCase,
)
from src.dependency import (
    RunTeamFormationUseCaseDependency,
    GetTeamFormationUseCaseDependency,
    ChooseTeamFormationVariantUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.team_formation.run")
async def run_team_formation(
    data: RunTeamFormationCommand,
    use_case: RunTeamFormationUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.team_formation.get")
async def get_team_formation(
    data: GetTeamFormationCommand,
    use_case: GetTeamFormationUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.team_formation.choose")
async def choose_team_formation_variant(
    data: ChooseTeamFormationVariantCommand,
    use_case: ChooseTeamFormationVariantUseCaseDependency,
) -> ResponseMessage:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
