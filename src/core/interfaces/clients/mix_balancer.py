from typing import Protocol
from uuid import UUID


class MixBalancerClientProtocol(Protocol):
    async def balance(
        self,
        draft_id: UUID,
        players: list[dict],
        balance_settings: dict,
    ) -> list[dict]: ...
