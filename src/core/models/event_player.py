from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .application import Application
    from .drafted_player import DraftedPlayer
    from .event import Event
    from .player_role import PlayerRole


class EventPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    member_id: UUID
    application_id: Optional[UUID] = None
    custom_id: Optional[UUID] = None
    is_draft_pinned: bool
    event: Optional[Event] = None
    application: Optional[Application] = None
    drafted_players: list[DraftedPlayer] = Field(default_factory=list)
    player_roles: list[PlayerRole] = Field(default_factory=list)
