from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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


class DraftedPlayerCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    draft_id: UUID
    event_player_id: UUID
    is_captain: bool | None = None
