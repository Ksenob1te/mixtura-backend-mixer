from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.event import EventMatchType, EventStatus, TeamFormation

from .common import AccessDataRequest, PaginationRequest


# ── Input message schemas (wire contract) ──────────────────────────────

class CreateEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    name: str
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    team_formation: TeamFormation
    allow_multiple_drafts: bool
    rating_set_id: UUID | None = None


class GetEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest


class ListEventsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    server_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class UpdateEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
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


class ActivateEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID


class OpenRegistrationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID


class CloseRegistrationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID


class CancelEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID


class CompleteEventMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID


# ── Output response schemas (wire contract) ────────────────────────────

class OrganizerResponse(BaseModel):
    id: UUID
    member_id: UUID


class RequiredIntegrationResponse(BaseModel):
    id: UUID
    provider_id: UUID


class SelectedGameRoleResponse(BaseModel):
    id: UUID
    game_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class ApplicationTimeSettingsResponse(BaseModel):
    id: UUID
    start_time: datetime | None = None
    end_time: datetime | None = None


class ApplicationCustomFieldResponse(BaseModel):
    id: UUID
    name: str
    is_private: bool
    is_required: bool


class ApplicationFormSettingsResponse(BaseModel):
    event_id: UUID
    event_name: str
    required_integrations: list[RequiredIntegrationResponse] = Field(default_factory=list)
    available_roles: list[SelectedGameRoleResponse] = Field(default_factory=list)
    custom_fields: list[ApplicationCustomFieldResponse] = Field(default_factory=list)
    time_settings: ApplicationTimeSettingsResponse | None = None


class EventCardResponse(BaseModel):
    id: UUID
    name: str
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    team_formation: TeamFormation
    status: EventStatus
    server_id: UUID


class EventDetailResponse(BaseModel):
    id: UUID
    name: str
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    team_formation: TeamFormation
    status: EventStatus
    allow_multiple_drafts: bool
    rating_set_id: UUID | None
    server_id: UUID
    organizers: list[OrganizerResponse] = Field(default_factory=list)
    required_integrations: list[RequiredIntegrationResponse] = Field(default_factory=list)
    selected_game_roles: list[SelectedGameRoleResponse] = Field(default_factory=list)
    time_settings: ApplicationTimeSettingsResponse | None = None
    custom_fields: list[ApplicationCustomFieldResponse] = Field(default_factory=list)
