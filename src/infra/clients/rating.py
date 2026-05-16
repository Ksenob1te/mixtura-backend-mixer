import json
from uuid import UUID

from faststream.rabbit import RabbitBroker

from src.core.interfaces.repo.rating import RatingClientProtocol
from src.core.models.rating import (
    MatchPlayerInput,
    MatchTeamInput,
    PlayerEffectiveRating,
    RatingPlayerRequest,
    RatingSettings,
)
from src.infra.rabbit.rpc_client import RabbitRpcClient


class RatingClient(RatingClientProtocol):
    def __init__(self, rpc_client: RabbitRpcClient, broker: RabbitBroker):
        self._rpc_client = rpc_client
        self._broker = broker

    async def calculate_effective_ratings(
        self,
        draft_id: UUID,
        players: list[RatingPlayerRequest],
        settings: RatingSettings | None = None,
    ) -> list[PlayerEffectiveRating]:
        response = await self._rpc_client.request(
            queue="rating.effective.calculate",
            payload={
                "draft_id": str(draft_id),
                "players": [_serialize_player_request(p) for p in players],
                "settings": settings.model_dump() if settings else None,
            },
        )
        body = json.loads(response.body.decode())
        raw_players = body.get("players", [])
        return [PlayerEffectiveRating(**p) for p in raw_players]

    async def process_match_result(
        self,
        match_id: UUID,
        match_time: str,
        teams: list[MatchTeamInput],
        team_ranks: list[float],
        players: list[MatchPlayerInput],
        settings: RatingSettings | None = None,
    ) -> None:
        await self._broker.publish(
            {
                "match_id": str(match_id),
                "match_time": match_time,
                "teams": [_serialize_match_team(t) for t in teams],
                "team_ranks": team_ranks,
                "players": [_serialize_match_player(p) for p in players],
                "settings": settings.model_dump() if settings else None,
            },
            queue="rating.match.process",
        )


def _serialize_player_request(player: RatingPlayerRequest) -> dict:
    return player.model_dump(mode="json")


def _serialize_match_team(team: MatchTeamInput) -> dict:
    return team.model_dump(mode="json")


def _serialize_match_player(player: MatchPlayerInput) -> dict:
    return player.model_dump(mode="json")
