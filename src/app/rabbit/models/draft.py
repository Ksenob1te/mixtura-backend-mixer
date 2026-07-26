from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.draft import DraftStatus
from src.core.models.event_player import EventPlayerStatus

from .common import AccessDataRequest, PaginationRequest


class CreateDraftMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    player_ids: list[UUID] | None = None
    statuses: list[EventPlayerStatus] | None = None
    limit: int | None = None
    pinned_only: bool = False


class GetDraftMessage(BaseModel):
    model_config = {"extra": "forbid"}
    draft_id: UUID
    access_data: AccessDataRequest


class ListDraftsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class DraftedPlayerItem(BaseModel):
    id: UUID
    draft_id: UUID
    event_player_id: UUID
    is_captain: bool | None = None


class DraftItem(BaseModel):
    id: UUID
    event_id: UUID
    status: DraftStatus


class DraftDetailResponse(BaseModel):
    id: UUID
    event_id: UUID
    status: DraftStatus
    drafted_players: list[DraftedPlayerItem] = Field(default_factory=list)
