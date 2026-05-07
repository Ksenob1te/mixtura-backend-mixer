from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .application import Application
    from .application_custom_field import ApplicationCustomField
    from .application_time_settings import ApplicationTimeSettings
    from .bracket import Bracket
    from .draft import Draft
    from .event_player import EventPlayer
    from .organizer import Organizer
    from .required_integration import RequiredIntegration
    from .selected_game_role import SelectedGameRole
    from .team import Team


class EventMatchType(str, enum.Enum):
    SINGLE = "SINGLE"
    TOURNAMENT = "TOURNAMENT"


class RegistrationType(str, enum.Enum):
    FREE = "FREE"
    APPLICATION = "APPLICATION"
    INVITE = "INVITE"


class EventStatus(str, enum.Enum):
    CREATED = "CREATED"
    REGISTRATION = "REGISTRATION"
    IDLE = "IDLE"
    FORMATION = "FORMATION"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TeamFormation(str, enum.Enum):
    DRAFT = "DRAFT"
    BALANCE = "BALANCE"
    MANUAL = "MANUAL"


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    registration_type: RegistrationType
    team_formation: TeamFormation
    status: EventStatus
    allow_multiple_drafts: bool
    rating_set_id: Optional[UUID] = None
    server_id: UUID
    applications: list[Application] = Field(default_factory=list)
    teams: list[Team] = Field(default_factory=list)
    drafts: list[Draft] = Field(default_factory=list)
    organizers: list[Organizer] = Field(default_factory=list)
    event_players: list[EventPlayer] = Field(default_factory=list)
    brackets: list[Bracket] = Field(default_factory=list)
    required_integrations: list[RequiredIntegration] = Field(default_factory=list)
    selected_game_roles: list[SelectedGameRole] = Field(default_factory=list)
    custom_fields: list[ApplicationCustomField] = Field(default_factory=list)
    time_settings: Optional[ApplicationTimeSettings] = None


class EventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    match_type: EventMatchType
    use_application: bool
    is_public: bool
    team_size: int
    registration_type: RegistrationType
    team_formation: TeamFormation
    allow_multiple_drafts: bool
    rating_set_id: UUID | None = None
    server_id: UUID


class EventUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    match_type: EventMatchType | None = None
    use_application: bool | None = None
    is_public: bool | None = None
    team_size: int | None = None
    registration_type: RegistrationType | None = None
    team_formation: TeamFormation | None = None
    allow_multiple_drafts: bool | None = None
    rating_set_id: UUID | None = None
