from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .match_slot import MatchSlot
    from .team import Team


class MatchScore(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    slot_id: UUID
    team_id: UUID
    score: int
    slot: Optional[MatchSlot] = None
    team: Optional[Team] = None


class MatchScoreCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    slot_id: UUID
    team_id: UUID
    score: int


class MatchScoreUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    score: int | None = None
