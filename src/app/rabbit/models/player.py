from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.event_player import EventPlayerStatus

from .common import AccessDataRequest, PaginationRequest
from .application import RolePriorityPayload


class ListPlayersMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    status: EventPlayerStatus | None = None
    pagination: PaginationRequest = PaginationRequest()


class AddPlayerMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    custom_id: UUID | None = None
    is_draft_pinned: bool = False


class UpdatePlayerStatusMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    status: EventPlayerStatus
    custom_id: UUID | None = None


class UpdatePlayerRolesMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
    role_priorities: list[RolePriorityPayload] = Field(default_factory=list)


class GetBulkPlayersMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    player_ids: list[UUID]


class RemovePlayerMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID


class PlayerItem(BaseModel):
    id: UUID
    member_id: UUID
    status: EventPlayerStatus
    is_draft_pinned: bool
    application_id: UUID | None = None
    custom_id: UUID | None = None


class PlayerAddResult(BaseModel):
    id: UUID
    event_id: UUID
    member_id: UUID
    status: EventPlayerStatus
    is_draft_pinned: bool
    application_id: UUID | None = None
    custom_id: UUID | None = None


class PlayerRoleItem(BaseModel):
    id: UUID
    game_role_id: UUID
    priority: int


class PlayerRolesUpdateResult(BaseModel):
    player_id: UUID
    roles: list[PlayerRoleItem]


class PlayerUpdateResult(BaseModel):
    id: UUID
    member_id: UUID
    status: EventPlayerStatus
    custom_id: UUID | None = None
