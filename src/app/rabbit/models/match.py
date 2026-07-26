from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .common import AccessDataRequest, PaginationRequest


class SetupMatchMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    team_ids: list[UUID]
    draft_id: UUID | None = None
    scheduled_at: datetime | None = None


class RecordMatchResultMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    match_id: UUID
    scores: dict[UUID, int]


class GetMatchMessage(BaseModel):
    model_config = {"extra": "forbid"}
    match_id: UUID
    access_data: AccessDataRequest


class ListMatchesMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    active: bool | None = None
    pagination: PaginationRequest = PaginationRequest()


class SingleMatchSlotView(BaseModel):
    slot_id: UUID
    slot_num: int
    team_id: UUID
    score_id: UUID
    score: int


class SingleMatchView(BaseModel):
    event_id: UUID
    bracket_id: UUID
    stage_id: UUID
    group_id: UUID
    match_id: UUID
    match_index: int
    draft_id: UUID | None = None
    completed_at: datetime | None = None
    slots: list[SingleMatchSlotView]
