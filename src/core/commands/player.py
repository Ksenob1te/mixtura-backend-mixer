from uuid import UUID

from pydantic import BaseModel, Field

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.application import RolePriorityPayload
from src.core.commands.pagination import PaginationRequest
from src.core.models.event_player import EventPlayerStatus


class ListPlayersCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest
    status: EventPlayerStatus | None = None
    pagination: PaginationRequest = PaginationRequest()


class AddPlayerCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    custom_id: UUID | None = None
    is_draft_pinned: bool = False


class UpdatePlayerStatusCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    status: EventPlayerStatus
    custom_id: UUID | None = None


class UpdatePlayerRolesCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    role_priorities: list[RolePriorityPayload] = Field(default_factory=list)


class GetBulkPlayersCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    player_ids: list[UUID]


class RemovePlayerCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
