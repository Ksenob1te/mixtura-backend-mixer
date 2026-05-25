from faststream.rabbit import RabbitRouter

from src.core.commands.player import (
    AddPlayerCommand,
    GetBulkPlayersCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    UpdatePlayerRolesCommand,
    UpdatePlayerStatusCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.core.results.player import PlayerAddResult, PlayerItem, PlayerRolesUpdateResult, PlayerUpdateResult
from src.dependency import PlayerServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.player.list")
async def list_players(
    data: ListPlayersCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[list[PlayerItem]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.add")
async def add_player(
    data: AddPlayerCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerAddResult]:
    result = await service.add(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.status.update")
async def update_player_status(
    data: UpdatePlayerStatusCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerUpdateResult]:
    result = await service.update_status(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.roles.update")
async def update_player_roles(
    data: UpdatePlayerRolesCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerRolesUpdateResult]:
    result = await service.update_roles(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.bulk_get")
async def bulk_get_players(
    data: GetBulkPlayersCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[list[PlayerItem]]:
    result = await service.get_bulk(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.player.remove")
async def remove_player(
    data: RemovePlayerCommand,
    service: PlayerServiceDependency,
) -> ResponseMessage[StatusResponse]:
    await service.remove(data)
    return ResponseMessage(status=200, message=StatusResponse())
