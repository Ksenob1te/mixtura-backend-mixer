from uuid import UUID

from faststream.rabbit import RabbitBroker

from src.core.interfaces.repo.balancer_request import BalancerRequestRepositoryProtocol
from src.core.models.balancer import BalancerPlayer, MixBalanceSettings, TournamentBalanceSettings


_BALANCER_REPLY_QUEUE = "mixer_service.balancer.result"


class BalancerRequestRepository(BalancerRequestRepositoryProtocol):
    def __init__(self, broker: RabbitBroker):
        self._broker = broker

    async def request_mix_formation(
        self,
        task_id: UUID,
        draft_id: UUID,
        players: list[BalancerPlayer],
        settings: MixBalanceSettings,
    ) -> None:
        await self._broker.publish(
            {
                "draft_id": str(draft_id),
                "players": [p.model_dump(mode="json") for p in players],
                "balance_settings": settings.model_dump(mode="json"),
            },
            queue="mix_balance_service.balance",
            correlation_id=str(task_id),
            reply_to=_BALANCER_REPLY_QUEUE,
        )

    async def request_tournament_formation(
        self,
        task_id: UUID,
        draft_id: UUID,
        players: list[BalancerPlayer],
        settings: TournamentBalanceSettings,
    ) -> None:
        await self._broker.publish(
            {
                "draft_id": str(draft_id),
                "players": [p.model_dump(mode="json") for p in players],
                "balance_settings": settings.model_dump(mode="json"),
            },
            queue="tournament_balance_service.balance",
            correlation_id=str(task_id),
            reply_to=_BALANCER_REPLY_QUEUE,
        )
