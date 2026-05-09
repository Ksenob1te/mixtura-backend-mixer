import json
from uuid import UUID

from faststream.rabbit import RabbitBroker

from src.core.interfaces.clients.rating import RatingClientProtocol


class RatingClient(RatingClientProtocol):
    def __init__(self, broker: RabbitBroker):
        self._broker = broker

    async def calculate_effective_ratings(
        self,
        draft_id: UUID,
        players: list[dict],
        settings: dict | None = None,
    ) -> list[dict]:
        response = await self._broker.request(
            {"draft_id": str(draft_id), "players": players, "settings": settings},
            queue="rating.effective.calculate",
            timeout=30.0,
        )
        body = json.loads(response.body.decode())
        return body.get("players", [])

    async def process_match_result(
        self,
        match_id: UUID,
        match_time: str,
        teams: list[dict],
        team_ranks: list[float],
        players: list[dict],
        settings: dict | None = None,
    ) -> None:
        await self._broker.publish(
            {
                "match_id": str(match_id),
                "match_time": match_time,
                "teams": teams,
                "team_ranks": team_ranks,
                "players": players,
                "settings": settings,
            },
            queue="rating.match.process",
        )
