from uuid import UUID

from pydantic import BaseModel, Field

from src.core.results.team_formation import RatingSnapshotPlayer


class BalancerTask(BaseModel):
    task_id: UUID
    draft_id: UUID
    event_id: UUID
    status: str
    event_player_by_member: dict[str, str] = Field(default_factory=dict)
    role_by_member: dict[str, str] = Field(default_factory=dict)
    rating_snapshot: list[RatingSnapshotPlayer] = Field(default_factory=list)
    error: str | None = None
