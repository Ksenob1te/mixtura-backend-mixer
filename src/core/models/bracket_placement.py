from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .bracket import Bracket
    from .team import Team


class BracketPlacement(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    bracket_id: UUID
    team_id: UUID
    placement: int
    bracket: Optional[Bracket] = None
    team: Optional[Team] = None
