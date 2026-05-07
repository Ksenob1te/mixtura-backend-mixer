from typing import Protocol
from uuid import UUID


class MixBalanceVariant(Protocol):
    id: UUID
    quality_uniformity: float
    quality_fairness: float
    quality_role_points: float
    quality_role_fairness: float


class MixBalancerClientProtocol(Protocol):
    async def balance(
        self,
        draft_id: UUID,
        players: list[dict],
        balance_settings: dict,
    ) -> list[MixBalanceVariant]: ...
