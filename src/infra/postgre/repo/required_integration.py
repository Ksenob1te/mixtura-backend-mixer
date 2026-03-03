from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RequiredIntegration
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class RequiredIntegrationRepository(BaseRepository):
    async def get_by_id(
            self,
            integration_id: UUID,
            load_event: bool = False
    ) -> RequiredIntegration | None:
        options = []
        if load_event:
            options.append(selectinload(RequiredIntegration.event))

        return await self._session.get(RequiredIntegration, integration_id, options=options)

    async def list_by_event(self, event_id: UUID) -> Sequence[RequiredIntegration]:
        stmt = select(RequiredIntegration).where(RequiredIntegration.event_id == event_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, integration: RequiredIntegration) -> RequiredIntegration:
        self._session.add(integration)
        await self._flush()
        await self._session.refresh(integration)
        return integration

    async def update(self, integration: RequiredIntegration) -> RequiredIntegration:
        integration = await self._session.merge(integration)
        await self._flush()
        return integration

    async def delete(self, integration_id: UUID) -> None:
        integration = await self.get_by_id(integration_id)
        if integration:
            await self._session.delete(integration)
            await self._flush()
