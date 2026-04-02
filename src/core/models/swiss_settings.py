from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .stage import Stage


class SwissSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    stage_id: UUID
    score_per_win: int
    score_per_draw: int
    score_per_bye: int
    stage: Optional[Stage] = None
