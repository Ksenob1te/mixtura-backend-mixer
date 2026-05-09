from typing import Protocol
from uuid import UUID


class RatingClientProtocol(Protocol):
    async def calculate_effective_ratings(
        self,
        draft_id: UUID,
        players: list[dict],
        settings: dict | None = None,
    ) -> list[dict]: ...

    async def process_match_result(
        self,
        match_id: UUID,
        match_time: str,
        teams: list[dict],
        team_ranks: list[float],
        players: list[dict],
        settings: dict | None = None,
    ) -> None: ...
