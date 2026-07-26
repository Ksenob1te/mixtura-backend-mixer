from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.player import (
    AddPlayerMessage,
    GetBulkPlayersMessage,
    ListPlayersMessage,
    PlayerAddResult,
    PlayerItem,
    PlayerRolesUpdateResult,
    PlayerUpdateResult,
    RemovePlayerMessage,
    UpdatePlayerRolesMessage,
    UpdatePlayerStatusMessage,
)
from src.core.commands.player import (
    AddPlayerCommand,
    GetBulkPlayersCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    UpdatePlayerRolesCommand,
    UpdatePlayerStatusCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.dependency import PlayerServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.player.list")
async def list_players(
    data: ListPlayersMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[list[PlayerItem]]:
    command = ListPlayersCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[PlayerItem(**r.model_dump()) for r in result])


@router.subscriber(queue="event.player.add")
async def add_player(
    data: AddPlayerMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerAddResult]:
    command = AddPlayerCommand(**data.model_dump())
    result = await service.add(command)
    return ResponseMessage(status=200, message=PlayerAddResult(**result.model_dump()))


@router.subscriber(queue="event.player.status.update")
async def update_player_status(
    data: UpdatePlayerStatusMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerUpdateResult]:
    command = UpdatePlayerStatusCommand(**data.model_dump())
    result = await service.update_status(command)
    return ResponseMessage(status=200, message=PlayerUpdateResult(**result.model_dump()))


@router.subscriber(queue="event.player.roles.update")
async def update_player_roles(
    data: UpdatePlayerRolesMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[PlayerRolesUpdateResult]:
    command = UpdatePlayerRolesCommand(**data.model_dump())
    result = await service.update_roles(command)
    return ResponseMessage(status=200, message=PlayerRolesUpdateResult(**result.model_dump()))


@router.subscriber(queue="event.player.bulk_get")
async def bulk_get_players(
    data: GetBulkPlayersMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[list[PlayerItem]]:
    command = GetBulkPlayersCommand(**data.model_dump())
    result = await service.get_bulk(command)
    return ResponseMessage(status=200, message=[PlayerItem(**r.model_dump()) for r in result])


@router.subscriber(queue="event.player.remove")
async def remove_player(
    data: RemovePlayerMessage,
    service: PlayerServiceDependency,
) -> ResponseMessage[StatusResponse]:
    command = RemovePlayerCommand(**data.model_dump())
    await service.remove(command)
    return ResponseMessage(status=200, message=StatusResponse())
