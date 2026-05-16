from typing import Protocol, runtime_checkable
from uuid import UUID

from src.core.results.balancer_task import BalancerTask


@runtime_checkable
class BalancerTaskStoreProtocol(Protocol):
    async def save(self, task: BalancerTask, ttl_seconds: int) -> None: ...

    async def get(self, task_id: UUID) -> BalancerTask | None: ...

    async def delete(self, task_id: UUID) -> None: ...
