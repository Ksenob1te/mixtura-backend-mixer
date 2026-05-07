from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .application_integration import ApplicationIntegration
    from .event import Event
    from .event_player import EventPlayer
    from .filled_application_field import FilledApplicationField


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WAITLIST = "WAITLIST"


class Application(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    member_id: UUID
    is_approved: bool
    status: ApplicationStatus
    event: Optional[Event] = None
    integrations: list[ApplicationIntegration] = Field(default_factory=list)
    filled_fields: list[FilledApplicationField] = Field(default_factory=list)
    event_player: Optional[EventPlayer] = None


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    member_id: UUID
    is_approved: bool = False
    status: ApplicationStatus = ApplicationStatus.PENDING


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    is_approved: bool | None = None
    status: ApplicationStatus | None = None
