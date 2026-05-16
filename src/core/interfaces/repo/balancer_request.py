from typing import Protocol
from uuid import UUID

from src.core.models.balancer import BalancerPlayer, MixBalanceSettings, TournamentBalanceSettings


class BalancerRequestRepositoryProtocol(Protocol):
    async def request_mix_formation(
        self,
        task_id: UUID,
        draft_id: UUID,
        players: list[BalancerPlayer],
        settings: MixBalanceSettings,
    ) -> None: ...

    async def request_tournament_formation(
        self,
        task_id: UUID,
        draft_id: UUID,
        players: list[BalancerPlayer],
        settings: TournamentBalanceSettings,
    ) -> None: ...
