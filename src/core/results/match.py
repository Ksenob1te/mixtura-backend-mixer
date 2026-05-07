from uuid import UUID

from pydantic import BaseModel


class MatchResultPayload(BaseModel):
    match_id: UUID
    match_time: str
    team_ids: list[UUID]
    team_ranks: list[float]
    player_ids: list[UUID]
    role_ids: list[UUID]
    open_ratings: list[float]
