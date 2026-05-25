from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BalancerPlayerRole(BaseModel):
    priority: int
    rating: int


class BalancerPlayer(BaseModel):
    member_id: UUID
    roles: dict[UUID, BalancerPlayerRole]


class MixRoleConfig(BaseModel):
    max_in_team: int
    min_in_team: int


class MixBalanceSettings(BaseModel):
    max_in_team: int
    roles: dict[UUID, MixRoleConfig] = Field(default_factory=dict)


class TournamentRoleConfig(BaseModel):
    count_in_team: int


class TournamentBalanceSettings(BaseModel):
    team_count: int
    players_in_team: int
    roles: dict[UUID, TournamentRoleConfig] = Field(default_factory=dict)
    priority: dict[str, int] = Field(default_factory=dict)


class BalancerTeamPlayer(BaseModel):
    member_id: UUID
    game_role_id: UUID
    rating: int
    priority: int = 0


class BalancerTeam(BaseModel):
    id: UUID
    players: list[BalancerTeamPlayer] = Field(default_factory=list)


class MixQualityMetrics(BaseModel):
    model_config = {"extra": "forbid"}

    uniformity: float
    fairness: float
    role_points: float
    role_fairness: float


class TournamentQualityMetrics(BaseModel):
    model_config = {"extra": "forbid"}

    dp_fairness: float = 0.0
    dp_role_fairness: float = 0.0
    vq_uniformity: float = 0.0
    role_priority_points: float = 0.0
    fitness_balance: float = 0.0
    fitness_priority: float = 0.0
    fitness_role_imbalance: float = 0.0
    fitness_team_spread: float = 0.0
    fitness_subrole: float = 0.0
    role_subrole_penalty: float = 0.0
    evaluation: float = 0.0


class MixBalance(BaseModel):
    id: UUID
    quality: MixQualityMetrics
    teams: list[BalancerTeam] = Field(default_factory=list)


class TournamentBalance(BaseModel):
    id: UUID
    quality: TournamentQualityMetrics
    teams: list[BalancerTeam] = Field(default_factory=list)


class MixBalancerResult(BaseModel):
    draft_id: UUID
    balances: list[MixBalance] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class TournamentBalancerResult(BaseModel):
    draft_id: UUID
    balances: list[TournamentBalance] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class BalancerResponse(BaseModel):
    status: int
    message: MixBalancerResult | TournamentBalancerResult
