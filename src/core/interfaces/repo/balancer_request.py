from typing import Protocol, runtime_checkable
from uuid import UUID

from src.core.models.balancer import BalancerPlayer, MixBalanceSettings, TournamentBalanceSettings


@runtime_checkable
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
