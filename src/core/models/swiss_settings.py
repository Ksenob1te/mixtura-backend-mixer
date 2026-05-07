from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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


class SwissSettingsCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    stage_id: UUID
    score_per_win: int
    score_per_draw: int
    score_per_bye: int


class SwissSettingsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    score_per_win: int | None = None
    score_per_draw: int | None = None
    score_per_bye: int | None = None
