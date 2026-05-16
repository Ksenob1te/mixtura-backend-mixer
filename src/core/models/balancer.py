from uuid import UUID

from pydantic import BaseModel, Field


class BalancerPlayerRole(BaseModel):
    priority: int
    rating: int


class BalancerPlayer(BaseModel):
    member_id: UUID
    roles: dict[str, BalancerPlayerRole]


class MixRoleConfig(BaseModel):
    count_in_team: int


class MixBalanceSettings(BaseModel):
    min_in_team: int
    max_in_team: int
    roles: dict[str, MixRoleConfig] = Field(default_factory=dict)


class TournamentRoleConfig(BaseModel):
    count_in_team: int
    min_count_in_team: int = 0
    max_count_in_team: int


class TournamentBalanceSettings(BaseModel):
    team_count: int
    players_in_team: int
    roles: dict[str, TournamentRoleConfig] = Field(default_factory=dict)
    priority: dict[str, int] = Field(default_factory=dict)
