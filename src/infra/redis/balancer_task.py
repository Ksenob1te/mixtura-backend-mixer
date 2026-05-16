from uuid import UUID

from redis.asyncio import Redis

from src.core.interfaces.repo.balancer_task import BalancerTaskStoreProtocol
from src.core.results.balancer_task import BalancerTask


class BalancerTaskStore(BalancerTaskStoreProtocol):
    def __init__(self, redis: Redis):
        self._redis = redis

    def _key(self, task_id: UUID) -> str:
        return f"balancer_task:{task_id}"

    async def save(self, task: BalancerTask, ttl_seconds: int) -> None:
        key = self._key(task.task_id)
        data = task.model_dump_json()
        await self._redis.set(key, data, ex=ttl_seconds)

    async def get(self, task_id: UUID) -> BalancerTask | None:
        key = self._key(task_id)
        data = await self._redis.get(key)
        if data is None:
            return None
        raw = data.decode() if isinstance(data, bytes) else data
        return BalancerTask.model_validate_json(raw)

    async def delete(self, task_id: UUID) -> None:
        key = self._key(task_id)
        await self._redis.delete(key)
