from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .stage import Stage


class RoundRobinSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    stage_id: UUID
    meetings_per_pair: int
    score_system: str
    score_per_win: Optional[int] = None
    score_per_draw: Optional[int] = None
    stage: Optional[Stage] = None
