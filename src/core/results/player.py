from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.core.models.event_player import EventPlayerStatus


class PlayerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    status: EventPlayerStatus
    is_draft_pinned: bool
    application_id: UUID | None = None
    custom_id: UUID | None = None


class PlayerAddResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    member_id: UUID
    status: EventPlayerStatus
    is_draft_pinned: bool
    application_id: UUID | None = None
    custom_id: UUID | None = None


class PlayerRoleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    game_role_id: UUID
    priority: int


class PlayerRolesUpdateResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id: UUID
    roles: list[PlayerRoleItem]


class PlayerUpdateResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    status: EventPlayerStatus
    custom_id: UUID | None = None
