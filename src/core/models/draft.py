from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .drafted_player import DraftedPlayer
    from .event import Event
    from .team import Team


class DraftStatus(str, enum.Enum):
    OPEN = 'OPEN'
    BALANCE_REQUESTED = 'BALANCE_REQUESTED'
    BALANCE_SELECTED = 'BALANCE_SELECTED'
    COMPLETED = 'COMPLETED'


class Draft(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    status: DraftStatus
    event: Optional[Event] = None
    teams: list[Team] = Field(default_factory=list)
    drafted_players: list[DraftedPlayer] = Field(default_factory=list)


class DraftCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    status: DraftStatus = DraftStatus.OPEN


class DraftUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    status: DraftStatus | None = None
