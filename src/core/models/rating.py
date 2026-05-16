from uuid import UUID

from pydantic import BaseModel, Field


class RatingSettings(BaseModel):
    """Rating system configuration parameters (mirrors mixtura-ranker RatingSettings)."""

    model_config = {"extra": "allow"}

    r_min: float = Field(default=0.0, description="Minimum open rating")
    r_max: float = Field(default=5000.0, description="Maximum open rating")
    r_avg: float = Field(default=2400.0, description="Expected open rating")
    g: float = Field(default=0.5, description="Player rating gravity")
    sigma_init: float = Field(default=25.0, description="Initial uncertainty")
    d: float = Field(default=4.0, description="Gate function steepness")

    @classmethod
    def from_command_dict(cls, raw: dict[str, str | int | float | bool | None] | None) -> "RatingSettings | None":
        if raw is None:
            return None
        return cls.model_validate({k: v for k, v in raw.items() if v is not None})


class RatingPlayerRequest(BaseModel):
    """Input player for effective rating calculation (mirrors mixtura-ranker Player)."""

    member_id: UUID = Field(..., description="Player ID")
    role_id: UUID = Field(..., description="Role ID")
    open_rating: float = Field(..., description="Open rating")
    priority: int = Field(default=0, description="Role priority (0 = minimal)")


class PlayerEffectiveRating(BaseModel):
    """Response from effective rating calculation (mirrors mixtura-ranker PlayerEffectiveRating)."""

    member_id: UUID = Field(..., description="Player ID")
    role_id: UUID = Field(..., description="Role ID")
    open_rating: float = Field(..., description="Open rating")
    effective_rating: float = Field(..., description="Effective rating")
    hidden_rating: float = Field(default=0.0, description="Projected hidden rating to open system")


class MatchTeamInput(BaseModel):
    """Team data for match result processing (mirrors mixtura-ranker MatchTeam)."""

    team_id: UUID = Field(..., description="Team ID")
    player_ids: list[UUID] = Field(..., description="Player IDs in the team")


class MatchPlayerInput(BaseModel):
    """Player data for match result processing (mirrors mixtura-ranker MatchPlayer)."""

    member_id: UUID = Field(..., description="Player ID")
    role_id: UUID = Field(..., description="Role ID")
    open_rating: float = Field(..., description="Open rating at match time")
