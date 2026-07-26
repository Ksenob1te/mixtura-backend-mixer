from uuid import UUID

from pydantic import BaseModel, Field

from .common import AccessDataRequest, PaginationRequest


class ListTeamsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class TeamPlayerItem(BaseModel):
    id: UUID
    team_id: UUID
    member_id: UUID
    game_role_id: UUID
    rating: float


class TeamItem(BaseModel):
    id: UUID
    event_id: UUID
    draft_id: UUID | None = None
    name: str


class TeamDetail(BaseModel):
    id: UUID
    event_id: UUID
    draft_id: UUID | None = None
    name: str
    players: list[TeamPlayerItem] = Field(default_factory=list)
