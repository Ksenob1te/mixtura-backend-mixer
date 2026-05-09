from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.event import EventMatchType, TeamFormation


class CreateEventCommand(BaseModel):
    access_data: AccessDataRequest
    name: str
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    team_formation: TeamFormation
    allow_multiple_drafts: bool
    rating_set_id: UUID | None = None


class GetEventCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None


class ListPublicEventsCommand(BaseModel):
    server_id: UUID
    pagination: PaginationRequest = PaginationRequest()


class ListPrivateEventsCommand(BaseModel):
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class UpdateEventCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    name: str | None = None
    match_type: EventMatchType | None = None
    use_application: bool | None = None
    is_public: bool | None = None
    team_size: int | None = None
    team_formation: TeamFormation | None = None
    allow_multiple_drafts: bool | None = None
    rating_set_id: UUID | None = None


class ActivateEventCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID


class OpenRegistrationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID


class CloseRegistrationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID


class CancelEventCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID


class CompleteEventCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
