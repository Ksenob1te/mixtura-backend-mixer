import json
from uuid import UUID

from redis.asyncio import Redis

from src.core.results.team_formation import TeamFormationJob


class TeamFormationVariantStore:
    def __init__(self, redis: Redis):
        self._redis = redis

    def _key(self, job_id: UUID, event_id: UUID, draft_id: UUID) -> str:
        return f"event:{event_id}:draft:{draft_id}:team_formation:{job_id}"

    def _latest_key(self, event_id: UUID, draft_id: UUID) -> str:
        return f"event:{event_id}:draft:{draft_id}:team_formation:latest"

    async def save(self, job_id: UUID, event_id: UUID, draft_id: UUID, payload: TeamFormationJob, ttl_seconds: int) -> None:
        key = self._key(job_id, event_id, draft_id)
        latest_key = self._latest_key(event_id, draft_id)
        data = payload.model_dump_json()
        await self._redis.set(key, data, ex=ttl_seconds)
        await self._redis.set(latest_key, str(job_id), ex=ttl_seconds)

    async def get(self, job_id: UUID, event_id: UUID, draft_id: UUID) -> TeamFormationJob | None:
        key = self._key(job_id, event_id, draft_id)
        data = await self._redis.get(key)
        if data is None:
            return None
        raw = data.decode() if isinstance(data, bytes) else data
        return TeamFormationJob.model_validate_json(raw)

    async def get_latest_by_draft(self, event_id: UUID, draft_id: UUID) -> TeamFormationJob | None:
        latest_key = self._latest_key(event_id, draft_id)
        job_id_str = await self._redis.get(latest_key)
        if job_id_str is None:
            return None
        raw = job_id_str.decode() if isinstance(job_id_str, bytes) else job_id_str
        try:
            job_id = UUID(raw)
        except ValueError:
            return None
        return await self.get(job_id, event_id, draft_id)

    async def delete(self, job_id: UUID, event_id: UUID, draft_id: UUID) -> None:
        key = self._key(job_id, event_id, draft_id)
        await self._redis.delete(key)
