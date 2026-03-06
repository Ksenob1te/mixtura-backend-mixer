from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import ApplicationTimeSettings
from .base import BaseRepository


class ApplicationTimeSettingsRepository(BaseRepository[ApplicationTimeSettings]):
    model = ApplicationTimeSettings

    async def get_by_event_id(
            self,
            event_id: UUID,
            load_event: bool = False
    ) -> ApplicationTimeSettings | None:
        stmt = select(ApplicationTimeSettings).where(ApplicationTimeSettings.event_id == event_id)

        if load_event:
            stmt = stmt.options(selectinload(ApplicationTimeSettings.event))

        return await self._session.scalar(stmt)

    async def delete_by_event_id(self, event_id: UUID) -> None:
        settings_field = await self.get_by_event_id(event_id)
        if settings_field:
            await self._session.delete(settings_field)
            await self._flush()
