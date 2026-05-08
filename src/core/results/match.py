from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
    result_snapshot: dict | None = None
    slots: list[SingleMatchSlotView]


class MatchResultPayload(BaseModel):
    match_id: UUID
    match_time: str
    team_ids: list[UUID]
    team_ranks: list[float]
    player_ids: list[UUID]
    role_ids: list[UUID]
    open_ratings: list[float]


class RecordedMatchResult(BaseModel):
    match: SingleMatchView
    winner_team_id: UUID | None = None
    loser_team_ids: list[UUID] = Field(default_factory=list)
    is_draw: bool = False
    forfeit_team_ids: list[UUID] = Field(default_factory=list)
    team_ranks: list[float]
    rating_payload: dict
    rating_published: bool
