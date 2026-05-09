from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest


class SetupMatchCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    team_ids: list[UUID]
    draft_id: UUID | None = None
    scheduled_at: datetime | None = None


class RecordMatchResultCommand(BaseModel):
    access_data: AccessDataRequest
    match_id: UUID
    scores: dict[UUID, int]
    winner_id: UUID | None = None
    is_draw: bool = False
    forfeit_team_ids: list[UUID] = Field(default_factory=list)
    rating_settings: dict[str, str | int | float | bool | None] | None = None


class GetMatchCommand(BaseModel):
    match_id: UUID
    access_data: AccessDataRequest | None = None


class ListMatchesCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    active: bool | None = None
    pagination: PaginationRequest = PaginationRequest()
