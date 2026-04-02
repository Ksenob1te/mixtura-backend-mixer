from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

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
