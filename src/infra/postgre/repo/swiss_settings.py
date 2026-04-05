from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import SwissSettingsModel
from .base import BaseRepository
from src.core.models.swiss_settings import SwissSettings


class SwissSettingsRepository(BaseRepository[SwissSettingsModel, SwissSettings]):
    model = SwissSettingsModel
    dto_model = SwissSettings

    async def get_by_stage_id(
            self,
            stage_id: UUID,
            load_stage: bool = False
    ) -> SwissSettings | None:
        stmt = select(SwissSettingsModel).where(SwissSettingsModel.stage_id == stage_id)

        if load_stage:
            stmt = stmt.options(selectinload(SwissSettingsModel.stage))

        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None

    async def delete_by_stage(self, stage_id: UUID) -> None:
        settings = await self._session.scalar(
            select(SwissSettingsModel).where(SwissSettingsModel.stage_id == stage_id)
        )
        if settings:
            await self._session.delete(settings)
            await self._flush()
