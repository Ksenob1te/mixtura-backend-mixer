from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamPlayerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    team_id: UUID
    member_id: UUID
    game_role_id: UUID
    rating: float


class TeamItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    draft_id: UUID | None = None
    name: str


class TeamDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    draft_id: UUID | None = None
    name: str
    players: list[TeamPlayerItem] = Field(default_factory=list)
