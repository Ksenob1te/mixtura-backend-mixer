from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.models.draft import DraftStatus


class DraftedPlayerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    draft_id: UUID
    event_player_id: UUID
    is_captain: bool | None = None


class DraftItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    status: DraftStatus


class DraftDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    status: DraftStatus
    drafted_players: list[DraftedPlayerItem] = Field(default_factory=list)
