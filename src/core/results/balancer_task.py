from uuid import UUID

from pydantic import BaseModel, Field


class RatingSnapshotPlayerFull(BaseModel):
    member_id: UUID
    event_player_id: UUID
    game_role_id: UUID
    priority: int
    open_rating: float
    calculated_rating: float
    effective_rating: float | None = None
    rating_source: str = "open"


class BalancerTask(BaseModel):
    task_id: UUID
    draft_id: UUID
    event_id: UUID
    status: str
    event_player_by_member: dict[UUID, UUID] = Field(default_factory=dict)
    role_by_member: dict[UUID, UUID] = Field(default_factory=dict)
    rating_snapshot: list[RatingSnapshotPlayerFull] = Field(default_factory=list)
    error: str | None = None
