from typing import Protocol
from uuid import UUID


class TournamentBalancerClientProtocol(Protocol):
    async def balance(
        self,
        draft_id: UUID,
        players: list[dict],
        balance_settings: dict,
    ) -> list[dict]: ...
