from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

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


class GetMatchCommand(BaseModel):
    match_id: UUID
    access_data: AccessDataRequest


class ListMatchesCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest
    active: bool | None = None
    pagination: PaginationRequest = PaginationRequest()
