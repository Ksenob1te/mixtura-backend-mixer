from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .bracket import Bracket
    from .round_robin_settings import RoundRobinSettings
    from .stage_group import StageGroup
    from .swiss_settings import SwissSettings


class StageFormat(str, enum.Enum):
    SINGLE_MATCH = "SINGLE_MATCH"
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION"
    DOUBLE_ELIMINATION = "DOUBLE_ELIMINATION"
    ROUND_ROBIN = "ROUND_ROBIN"
    SWISS = "SWISS"


class Stage(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    stage_index: int
    format: StageFormat
    name: str
    bracket_id: UUID
    bracket: Optional[Bracket] = None
    groups: list[StageGroup] = Field(default_factory=list)
    round_robin_settings: Optional[RoundRobinSettings] = None
    swiss_settings: Optional[SwissSettings] = None


class StageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    stage_index: int
    format: StageFormat
    name: str
    bracket_id: UUID


class StageUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    format: StageFormat | None = None
    name: str | None = None
