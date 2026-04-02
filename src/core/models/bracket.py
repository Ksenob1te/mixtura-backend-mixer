from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

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
