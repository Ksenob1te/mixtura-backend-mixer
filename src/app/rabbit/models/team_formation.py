from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.balancer import MixQualityMetrics, TournamentQualityMetrics

from .common import AccessDataRequest, PaginationRequest


class RatingSnapshotInput(BaseModel):
    member_id: UUID
    event_player_id: UUID | None = None
    game_role_id: UUID
    priority: int = 1
    open_rating: float


class RunTeamFormationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    draft_id: UUID
    use_effective_rating: bool = False
    rating_snapshot: list[RatingSnapshotInput] = Field(default_factory=list)
    rating_settings: dict | None = None
    team_count: int | None = None


class GetTeamFormationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    draft_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class ChooseTeamFormationVariantMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    draft_id: UUID
    variant_id: UUID


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
