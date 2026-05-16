from typing import Protocol, runtime_checkable
from uuid import UUID

from src.core.models.rating import (
    MatchPlayerInput,
    MatchTeamInput,
    PlayerEffectiveRating,
    RatingPlayerRequest,
    RatingSettings,
)


@runtime_checkable
class RatingClientProtocol(Protocol):
    async def calculate_effective_ratings(
        self,
        draft_id: UUID,
        players: list[RatingPlayerRequest],
        settings: RatingSettings | None = None,
    ) -> list[PlayerEffectiveRating]: ...

    async def process_match_result(
        self,
        match_id: UUID,
        match_time: str,
        teams: list[MatchTeamInput],
        team_ranks: list[float],
        players: list[MatchPlayerInput],
        settings: RatingSettings | None = None,
    ) -> None: ...
