from faststream.rabbit import RabbitRouter

from src.core.commands.player import (
    ListPlayersCommand,
    RemovePlayerCommand,
    UpdatePlayerStatusCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.dependency import PlayerServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.player.list")
async def list_players(
    data: ListPlayersCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[list[dict]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.status.update")
async def update_player_status(
    data: UpdatePlayerStatusCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[dict]:
    result = await service.update_status(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.remove")
async def remove_player(
    data: RemovePlayerCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[StatusResponse]:
    await service.remove(data)
    return ResponseMessage(status=200, message=StatusResponse())
