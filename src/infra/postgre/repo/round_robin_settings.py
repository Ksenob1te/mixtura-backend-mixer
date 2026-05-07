from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.interfaces.repo.round_robin_settings import RoundRobinSettingsRepositoryProtocol
from src.core.models.round_robin_settings import RoundRobinSettings, RoundRobinSettingsCreate, RoundRobinSettingsUpdate
from .base import BaseRepository
from ..models import RoundRobinSettingsModel


class RoundRobinSettingsRepository(RoundRobinSettingsRepositoryProtocol,
                                   BaseRepository[RoundRobinSettingsModel, RoundRobinSettingsCreate, RoundRobinSettings, RoundRobinSettingsUpdate]):
    model = RoundRobinSettingsModel
    dto_model = RoundRobinSettings

    async def get_by_stage_id(
            self,
            stage_id: UUID,
            load_stage: bool = False
    ) -> RoundRobinSettings | None:
        stmt = select(RoundRobinSettingsModel).where(RoundRobinSettingsModel.stage_id == stage_id)

        if load_stage:
            stmt = stmt.options(selectinload(RoundRobinSettingsModel.stage))

        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None

    async def delete_by_stage(self, stage_id: UUID) -> None:
        settings = await self._session.scalar(
            select(RoundRobinSettingsModel).where(RoundRobinSettingsModel.stage_id == stage_id)
        )
        if settings:
            await self._session.delete(settings)
            await self._flush()
