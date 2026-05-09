from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .event import Event
    from .player_role import PlayerRole
    from .team_player import TeamPlayer


class SelectedGameRole(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    game_role_id: UUID
    event_id: UUID
    override_max_count: Optional[int] = None
    override_min_count: Optional[int] = None
    event: Optional[Event] = None
    player_roles: list[PlayerRole] = Field(default_factory=list)
    team_players: list[TeamPlayer] = Field(default_factory=list)


class SelectedGameRoleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    game_role_id: UUID
    event_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class SelectedGameRoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None
