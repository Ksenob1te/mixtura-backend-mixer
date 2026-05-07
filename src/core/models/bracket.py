from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .bracket_placement import BracketPlacement
    from .event import Event
    from .stage import Stage


class Bracket(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    event: Optional[Event] = None
    stages: list[Stage] = Field(default_factory=list)
    placements: list[BracketPlacement] = Field(default_factory=list)


class BracketCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
