from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import ApplicationTimeSettingsModel
from .base import BaseRepository
from src.core.models.application_time_settings import ApplicationTimeSettings

from src.core.interfaces.repo.application_time_settings import ApplicationTimeSettingsRepositoryProtocol


class ApplicationTimeSettingsRepository(ApplicationTimeSettingsRepositoryProtocol,
                                        BaseRepository[ApplicationTimeSettingsModel, ApplicationTimeSettings]):
    model = ApplicationTimeSettingsModel
    dto_model = ApplicationTimeSettings

    async def get_by_event_id(
            self,
            event_id: UUID,
            load_event: bool = False
    ) -> ApplicationTimeSettings | None:
        stmt = select(ApplicationTimeSettingsModel).where(ApplicationTimeSettingsModel.event_id == event_id)

        if load_event:
            stmt = stmt.options(selectinload(ApplicationTimeSettingsModel.event))

        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None

    async def delete_by_event_id(self, event_id: UUID) -> None:
        settings_field = await self._session.scalar(
            select(ApplicationTimeSettingsModel).where(ApplicationTimeSettingsModel.event_id == event_id)
        )
        if settings_field:
            await self._session.delete(settings_field)
            await self._flush()
