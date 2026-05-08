from uuid import UUID

from pydantic import BaseModel, Field


class RatingSnapshotPlayer(BaseModel):
    member_id: UUID
    event_player_id: UUID
    game_role_id: UUID
    priority: int
    open_rating: float
    calculated_rating: float
    effective_rating: float | None = None
    rating_source: str = "open"


class TeamFormationVariantTeam(BaseModel):
    team_index: int
    name: str
    member_ids: list[UUID]
    event_player_ids: list[UUID]
    game_role_ids: list[UUID]
    calculated_ratings: list[float]


class TeamFormationVariantMetrics(BaseModel):
    strength_diff: float = 0.0
    role_fit: float = 0.0
    rating_spread: float = 0.0
    constraint_violations: int = 0
    raw_metrics: dict[str, float] = Field(default_factory=dict)


class TeamFormationVariant(BaseModel):
    id: UUID
    draft_id: UUID
    teams: list[TeamFormationVariantTeam] = Field(default_factory=list)
    metrics: TeamFormationVariantMetrics = Field(default_factory=TeamFormationVariantMetrics)
    is_selected: bool = False


class TeamFormationJob(BaseModel):
    job_id: UUID
    draft_id: UUID
    event_id: UUID
    status: str
    variants: list[TeamFormationVariant] = Field(default_factory=list)
    rating_snapshot: list[RatingSnapshotPlayer] = Field(default_factory=list)
    error: str | None = None
