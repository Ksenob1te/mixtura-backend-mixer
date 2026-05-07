from typing import Protocol
from uuid import UUID


class TournamentBalanceVariant(Protocol):
    id: UUID
    dp_fairness: float
    dp_role_fairness: float
    vq_uniformity: float
    role_priority_points: float


class TournamentBalancerClientProtocol(Protocol):
    async def balance(
        self,
        draft_id: UUID,
        players: list[dict],
        balance_settings: dict,
    ) -> list[TournamentBalanceVariant]: ...
