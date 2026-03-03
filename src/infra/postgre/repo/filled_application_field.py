from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import FilledApplicationField
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException
from .base import BaseRepository


class FilledApplicationFieldRepository(BaseRepository):
    async def get_by_id(
            self,
            filled_id: UUID,
            load_application: bool = False,
            load_custom_field: bool = False
    ) -> FilledApplicationField | None:
        options = []
        if load_application:
            options.append(selectinload(FilledApplicationField.application))
        if load_custom_field:
            options.append(selectinload(FilledApplicationField.custom_field))

        return await self._session.get(FilledApplicationField, filled_id, options=options)

    async def list_by_application(self, application_id: UUID) -> Sequence[FilledApplicationField]:
        stmt = select(FilledApplicationField).where(FilledApplicationField.application_id == application_id)
        result = await self._session.scalars(stmt)
        return result.all()

    async def create(self, field: FilledApplicationField) -> FilledApplicationField:
        self._session.add(field)
        await self._flush()
        await self._session.refresh(field)
        return field

    async def update(self, field: FilledApplicationField) -> FilledApplicationField:
        field = await self._session.merge(field)
        await self._flush()
        return field

    async def delete(self, filled_id: UUID) -> None:
        field = await self.get_by_id(filled_id)
        if field:
            await self._session.delete(field)
            await self._flush()
