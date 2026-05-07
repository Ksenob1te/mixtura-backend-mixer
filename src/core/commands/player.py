from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.event_player import EventPlayerStatus


class ListPlayersCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    status: EventPlayerStatus | None = None
    pagination: PaginationRequest = PaginationRequest()


class UpdatePlayerStatusCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    status: EventPlayerStatus


class RemovePlayerCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
