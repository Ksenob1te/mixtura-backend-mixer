from faststream.rabbit import RabbitRouter

from src.core.commands.player import (
    ListPlayersCommand,
    RemovePlayerCommand,
    UpdatePlayerStatusCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.core.usecases.player import (
    ListPlayersUseCase,
    RemovePlayerUseCase,
    UpdatePlayerStatusUseCase,
)
from src.dependency import (
    ListPlayersUseCaseDependency,
    RemovePlayerUseCaseDependency,
    UpdatePlayerStatusUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.player.list")
async def list_players(
    data: ListPlayersCommand,
    use_case: ListPlayersUseCaseDependency,
) -> ResponseMessage[list[dict]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.status.update")
async def update_player_status(
    data: UpdatePlayerStatusCommand,
    use_case: UpdatePlayerStatusUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.remove")
async def remove_player(
    data: RemovePlayerCommand,
    use_case: RemovePlayerUseCaseDependency,
) -> ResponseMessage[StatusResponse]:
    await use_case(data)
    return ResponseMessage(status=200, message=StatusResponse())
