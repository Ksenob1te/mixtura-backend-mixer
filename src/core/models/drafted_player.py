from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .draft import Draft
    from .event_player import EventPlayer


class DraftedPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    draft_id: UUID
    event_player_id: UUID
    is_captain: Optional[bool] = None
    draft: Optional[Draft] = None
    event_player: Optional[EventPlayer] = None
