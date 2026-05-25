from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.balancer import MixQualityMetrics, TournamentQualityMetrics


class RatingSnapshotPlayer(BaseModel):
    member_id: UUID
    event_player_id: UUID
    game_role_id: UUID
    priority: int
    open_rating: float
    rating_source: str = "open"


class TeamFormationVariantTeam(BaseModel):
    team_index: int
    name: str
    member_ids: list[UUID]
    event_player_ids: list[UUID]
    game_role_ids: list[UUID]
    calculated_ratings: list[float]


class TeamFormationVariant(BaseModel):
    id: UUID
    draft_id: UUID
    teams: list[TeamFormationVariantTeam] = Field(default_factory=list)
    metrics: MixQualityMetrics | TournamentQualityMetrics
    is_selected: bool = False


class TeamFormationJob(BaseModel):
    job_id: UUID
    draft_id: UUID
    event_id: UUID
    status: str
    variants: list[TeamFormationVariant] = Field(default_factory=list)
    rating_snapshot: list[RatingSnapshotPlayer] = Field(default_factory=list)
    error: str | None = None
