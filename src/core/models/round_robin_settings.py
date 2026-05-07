from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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


class RoundRobinSettingsCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    stage_id: UUID
    meetings_per_pair: int
    score_system: str
    score_per_win: int | None = None
    score_per_draw: int | None = None


class RoundRobinSettingsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    meetings_per_pair: int | None = None
    score_system: str | None = None
    score_per_win: int | None = None
    score_per_draw: int | None = None
