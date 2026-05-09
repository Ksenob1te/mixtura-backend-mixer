from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .application import Application
    from .drafted_player import DraftedPlayer
    from .event import Event
    from .player_role import PlayerRole


class EventPlayerStatus(str, enum.Enum):
    REGISTERED = "REGISTERED"
    SELECTED = "SELECTED"
    PLAYING = "PLAYING"
    COMPLETED = "COMPLETED"
    BENCHED = "BENCHED"


class EventPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    member_id: UUID
    application_id: Optional[UUID] = None
    custom_id: Optional[UUID] = None
    is_draft_pinned: bool
    status: EventPlayerStatus
    event: Optional[Event] = None
    application: Optional[Application] = None
    drafted_players: list[DraftedPlayer] = Field(default_factory=list)
    player_roles: list[PlayerRole] = Field(default_factory=list)


class EventPlayerCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    member_id: UUID
    application_id: UUID | None = None
    custom_id: UUID | None = None
    is_draft_pinned: bool = False


class EventPlayerUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    is_draft_pinned: bool | None = None
    status: EventPlayerStatus | None = None
