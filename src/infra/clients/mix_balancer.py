import json
from uuid import UUID

from faststream.rabbit import RabbitBroker

from src.core.interfaces.clients.mix_balancer import MixBalancerClientProtocol


class MixBalancerClient(MixBalancerClientProtocol):
    def __init__(self, broker: RabbitBroker):
        self._broker = broker

    async def balance(
        self,
        draft_id: UUID,
        players: list[dict],
        balance_settings: dict,
    ) -> list[dict]:
        response = await self._broker.request(
            {"draft_id": str(draft_id), "players": players, "balance_settings": balance_settings},
            queue="mix_balance_service.balance",
            timeout=30.0,
        )
        body = json.loads(response.body.decode())
        return body.get("variants", [])
