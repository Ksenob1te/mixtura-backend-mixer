from typing import Protocol
from uuid import UUID


class EffectiveRatingPlayer(Protocol):
    member_id: UUID
    role_id: UUID
    open_rating: float
    effective_rating: float
    hidden_rating: float


class MatchResultPlayer(Protocol):
    member_id: UUID
    role_id: UUID
    open_rating: float


class RatingClientProtocol(Protocol):
    async def calculate_effective_ratings(
        self,
        draft_id: UUID,
        players: list[dict],
        settings: dict | None = None,
    ) -> list[EffectiveRatingPlayer]: ...

    async def process_match_result(
        self,
        match_id: UUID,
        match_time: str,
        teams: list[dict],
        team_ranks: list[float],
        players: list[MatchResultPlayer],
        settings: dict | None = None,
    ) -> None: ...
