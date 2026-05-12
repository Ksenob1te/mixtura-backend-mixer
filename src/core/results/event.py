from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.models.event import EventMatchType, EventStatus, TeamFormation


class OrganizerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID


class RequiredIntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str


class SelectedGameRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    game_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class ApplicationTimeSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    start_time: datetime | None = None
    end_time: datetime | None = None


class ApplicationCustomFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    is_private: bool
    is_required: bool


class ApplicationFormSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_id: UUID
    event_name: str
    required_integrations: list[RequiredIntegrationResponse] = Field(default_factory=list)
    available_roles: list[SelectedGameRoleResponse] = Field(default_factory=list)
    custom_fields: list[ApplicationCustomFieldResponse] = Field(default_factory=list)
    time_settings: ApplicationTimeSettingsResponse | None = None


class EventCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    team_formation: TeamFormation
    status: EventStatus
    server_id: UUID


class EventDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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
