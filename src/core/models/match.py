from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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
    result_snapshot: dict | None = None
    group: Optional[StageGroup] = None
    slots: list[MatchSlot] = Field(default_factory=list)
    source_slots: list[MatchSlot] = Field(default_factory=list)


class MatchCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    group_id: UUID | None = None
    match_index: int | None = None
    scheduled_at: datetime | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None
    round_number: int | None = None
    bracket_position: BracketPosition | None = None
    result_snapshot: dict | None = None


class MatchUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    scheduled_at: datetime | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None
    round_number: int | None = None
    bracket_position: BracketPosition | None = None
    result_snapshot: dict | None = None
