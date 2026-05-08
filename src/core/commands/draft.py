from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.event_player import EventPlayerStatus


class CreateDraftCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    player_ids: list[UUID] | None = None
    statuses: list[EventPlayerStatus] | None = None
    limit: int | None = None
    pinned_only: bool = False


class GetDraftCommand(BaseModel):
    draft_id: UUID
    access_data: AccessDataRequest | None = None


class ListDraftsCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    pagination: PaginationRequest = PaginationRequest()
