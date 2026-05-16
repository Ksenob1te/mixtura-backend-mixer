from typing import Protocol, runtime_checkable
from uuid import UUID

from src.core.results.team_formation import TeamFormationJob


@runtime_checkable
class TeamFormationVariantStoreProtocol(Protocol):
    async def save(self, job_id: UUID, event_id: UUID, draft_id: UUID, payload: TeamFormationJob, ttl_seconds: int) -> None: ...

    async def get(self, job_id: UUID, event_id: UUID, draft_id: UUID) -> TeamFormationJob | None: ...

    async def get_latest_by_draft(self, event_id: UUID, draft_id: UUID) -> TeamFormationJob | None: ...

    async def delete(self, job_id: UUID, event_id: UUID, draft_id: UUID) -> None: ...
