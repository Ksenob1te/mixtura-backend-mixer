from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .match import Match
    from .stage import Stage


class StageGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    stage_id: UUID
    name: str
    advance_count: Optional[int] = None
    stage: Optional[Stage] = None
    matches: list[Match] = Field(default_factory=list)


class StageGroupCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    stage_id: UUID
    name: str
    advance_count: int | None = None


class StageGroupUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    name: str | None = None
    advance_count: int | None = None
