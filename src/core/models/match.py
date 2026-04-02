from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .match_slot import MatchSlot
    from .stage_group import StageGroup


class BracketPosition(str, enum.Enum):
    UPPER = "UPPER"
    LOWER = "LOWER"


class Match(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    group_id: Optional[UUID] = None
    match_index: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    round_number: Optional[int] = None
    bracket_position: Optional[BracketPosition] = None
    group: Optional[StageGroup] = None
    slots: list[MatchSlot] = Field(default_factory=list)
    source_slots: list[MatchSlot] = Field(default_factory=list)
