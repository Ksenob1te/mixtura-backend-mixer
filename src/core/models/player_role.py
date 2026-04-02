from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .event_player import EventPlayer
    from .selected_game_role import SelectedGameRole


class PlayerRole(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    game_role_id: UUID
    priority: int
    event_player_id: UUID
    game_role: Optional[SelectedGameRole] = None
    event_player: Optional[EventPlayer] = None
