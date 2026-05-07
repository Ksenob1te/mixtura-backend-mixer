from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.core.models.event import EventMatchType, EventStatus, RegistrationType, TeamFormation


class EventCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    match_type: EventMatchType
    is_public: bool
    team_size: int
    registration_type: RegistrationType
    team_formation: TeamFormation
    status: EventStatus
    server_id: UUID


class EventDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    registration_type: RegistrationType
    team_formation: TeamFormation
    status: EventStatus
    allow_multiple_drafts: bool
    rating_set_id: UUID | None
    server_id: UUID
