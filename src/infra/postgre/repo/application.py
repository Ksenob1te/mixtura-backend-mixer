from uuid import UUID
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models import ApplicationModel
from ..models.application import ApplicationStatus
from .base import BaseRepository


class ApplicationRepository(BaseRepository[ApplicationModel]):
    model = ApplicationModel

    async def get(
            self,
            field_id: UUID,
            load_filled_fields: bool = False,
            load_integrations: bool = False,
            load_event_player: bool = False
    ) -> ApplicationModel | None:
        options = []
        if load_filled_fields:
            options.append(selectinload(ApplicationModel.filled_fields))
        if load_integrations:
            options.append(selectinload(ApplicationModel.integrations))
        if load_event_player:
            options.append(selectinload(ApplicationModel.event_player))

        return await super()._get(field_id, options=options)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> ApplicationModel | None:
        stmt = select(ApplicationModel).where(
            ApplicationModel.event_id == event_id,
            ApplicationModel.member_id == member_id,
        )
        return await self._session.scalar(stmt)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[ApplicationModel]:
        return await self.list(
            offset, limit, None,
            ApplicationModel.event_id == event_id
        )

    async def count_by_event_and_status(self, event_id: UUID, status: ApplicationStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(ApplicationModel)
            .where(ApplicationModel.event_id == event_id, ApplicationModel.status == status)
        )
        return (await self._session.scalar(stmt)) or 0

