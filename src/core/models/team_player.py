from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .selected_game_role import SelectedGameRole
    from .team import Team


class TeamPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    team_id: UUID
    member_id: UUID
    game_role_id: UUID
    rating: float
    team: Optional[Team] = None
    game_role: Optional[SelectedGameRole] = None
