from uuid import UUID

from pydantic import BaseModel, Field

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.rating import RatingSettings


class RatingSnapshotInput(BaseModel):
    member_id: UUID
    event_player_id: UUID | None = None
    game_role_id: UUID
    priority: int = 1
    open_rating: float


class RunTeamFormationCommand(BaseModel):
    access_data: AccessDataRequest
    draft_id: UUID
    use_effective_rating: bool = False
    rating_snapshot: list[RatingSnapshotInput] = Field(default_factory=list)
    rating_settings: RatingSettings | None = None
    team_count: int | None = None


class GetTeamFormationCommand(BaseModel):
    draft_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class ChooseTeamFormationVariantCommand(BaseModel):
    access_data: AccessDataRequest
    draft_id: UUID
    variant_id: UUID
