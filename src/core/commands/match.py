from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest


class SetupMatchCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    team_ids: list[UUID]


class RecordMatchResultCommand(BaseModel):
    access_data: AccessDataRequest
    match_id: UUID
    scores: dict[UUID, int]
    winner_id: UUID | None = None
    is_draw: bool = False


class GetMatchCommand(BaseModel):
    match_id: UUID
    access_data: AccessDataRequest | None = None


class ListMatchesCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    pagination: PaginationRequest = PaginationRequest()
