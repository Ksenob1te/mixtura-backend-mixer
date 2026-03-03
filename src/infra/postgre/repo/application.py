from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models import Application
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class ApplicationRepository(BaseRepository):
    async def get_by_id(
            self,
            application_id: UUID,
            load_filled_fields: bool = False,
            load_integrations: bool = False,
            load_event_player: bool = False
    ) -> Application | None:
        options = []
        if load_filled_fields:
            options.append(selectinload(Application.filled_fields))
        if load_integrations:
            options.append(selectinload(Application.integrations))
        if load_event_player:
            options.append(selectinload(Application.event_player))

        return await self._session.get(Application, application_id, options=options)

    async def list_by_event(self, event_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Application]:
        stmt = (
            select(Application)
            .where(Application.event_id == event_id)
            .offset(skip).limit(limit)
        )
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, application: Application) -> Application:
        self._session.add(application)
        await self._flush()
        await self._session.refresh(application)
        return application

    async def update(self, application: Application) -> Application:
        application = await self._session.merge(application)
        await self._flush()
        return application

    async def delete(self, application_id: UUID) -> None:
        application = await self.get_by_id(application_id)
        if application:
            await self._session.delete(application)
            await self._flush()
