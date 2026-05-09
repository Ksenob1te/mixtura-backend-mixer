from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .match import Match
    from .match_score import MatchScore
    from .stage_group import StageGroup


class MatchSlotSourceType(str, enum.Enum):
    WINNER_OF = "WINNER_OF"
    LOSER_OF = "LOSER_OF"
    GROUP_PLACEMENT = "GROUP_PLACEMENT"
    MANUAL = "MANUAL"
    AUTO = "AUTO"


class MatchSlot(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    match_id: UUID
    slot_num: int
    source_type: MatchSlotSourceType
    source_match_id: Optional[UUID] = None
    source_group_id: Optional[UUID] = None
    group_placement: Optional[int] = None
    match: Optional[Match] = None
    source_match: Optional[Match] = None
    source_group: Optional[StageGroup] = None
    score: Optional[MatchScore] = None


class MatchSlotCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    match_id: UUID
    slot_num: int
    source_type: MatchSlotSourceType
    source_match_id: UUID | None = None
    source_group_id: UUID | None = None
    group_placement: int | None = None
