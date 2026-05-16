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


class PlayerUpdateResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    status: EventPlayerStatus
    custom_id: UUID | None = None
