from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .draft import Draft
    from .event import Event
    from .team_player import TeamPlayer


class Team(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    draft_id: Optional[UUID] = None
    name: str
    event: Optional[Event] = None
    draft: Optional[Draft] = None
    players: list[TeamPlayer] = Field(default_factory=list)


class TeamCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    draft_id: UUID | None = None
    name: str


class TeamUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    name: str | None = None
