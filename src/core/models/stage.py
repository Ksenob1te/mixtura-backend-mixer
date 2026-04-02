from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .bracket import Bracket
    from .round_robin_settings import RoundRobinSettings
    from .stage_group import StageGroup
    from .swiss_settings import SwissSettings


class Stage(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    stage_index: int
    format: str
    name: str
    bracket_id: UUID
    bracket: Optional[Bracket] = None
    groups: list[StageGroup] = Field(default_factory=list)
    round_robin_settings: Optional[RoundRobinSettings] = None
    swiss_settings: Optional[SwissSettings] = None
