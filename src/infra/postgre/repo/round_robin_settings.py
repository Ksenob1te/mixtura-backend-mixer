from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import RoundRobinSettingsModel
from .base import BaseRepository


class RoundRobinSettingsRepository(BaseRepository[RoundRobinSettingsModel]):
    model = RoundRobinSettingsModel

    async def get_by_stage_id(
            self,
            stage_id: UUID,
            load_stage: bool = False
    ) -> RoundRobinSettingsModel | None:
        stmt = select(RoundRobinSettingsModel).where(RoundRobinSettingsModel.stage_id == stage_id)

        if load_stage:
            stmt = stmt.options(selectinload(RoundRobinSettingsModel.stage))

        return await self._session.scalar(stmt)

    async def delete_by_stage(self, stage_id: UUID) -> None:
        settings = await self.get_by_stage_id(stage_id)
        if settings:
            await self._session.delete(settings)
            await self._flush()
