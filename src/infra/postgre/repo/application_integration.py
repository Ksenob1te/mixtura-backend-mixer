from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import ApplicationIntegration
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class ApplicationIntegrationRepository(BaseRepository):
    async def get_by_id(
            self,
            integration_id: UUID,
            load_application: bool = False
    ) -> ApplicationIntegration | None:
        options = []
        if load_application:
            options.append(selectinload(ApplicationIntegration.application))

        return await self._session.get(ApplicationIntegration, integration_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[ApplicationIntegration]:
        stmt = select(ApplicationIntegration).where(ApplicationIntegration.application_id == application_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, integration: ApplicationIntegration) -> ApplicationIntegration:
        self._session.add(integration)
        await self._flush()
        await self._session.refresh(integration)
        return integration

    async def update(self, integration: ApplicationIntegration) -> ApplicationIntegration:
        integration = await self._session.merge(integration)
        await self._flush()
        return integration

    async def delete(self, integration_id: UUID) -> None:
        integration = await self.get_by_id(integration_id)
        if integration:
            await self._session.delete(integration)
            await self._flush()
