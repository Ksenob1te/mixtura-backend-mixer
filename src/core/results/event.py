from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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
    organizers: list[OrganizerResponse] = []
    required_integrations: list[RequiredIntegrationResponse] = []
    selected_game_roles: list[SelectedGameRoleResponse] = []
    time_settings: ApplicationTimeSettingsResponse | None = None
    custom_fields: list[ApplicationCustomFieldResponse] = []
