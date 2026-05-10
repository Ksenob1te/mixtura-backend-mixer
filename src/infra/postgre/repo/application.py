from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundException
from src.core.interfaces.repo.application import ApplicationRepositoryProtocol
from src.core.models.application import Application, ApplicationCreate, ApplicationStatus, ApplicationUpdate
from .base import BaseRepository
from ..models import ApplicationModel, EventPlayerModel, PlayerRoleModel


class ApplicationRepository(BaseRepository[ApplicationModel, ApplicationCreate, Application, ApplicationUpdate],
                            ApplicationRepositoryProtocol):
    model = ApplicationModel
    dto_model = Application

    async def get(
            self,
            field_id: UUID,
            load_filled_fields: bool = False,
            load_integrations: bool = False,
            load_event_player: bool = False
    ) -> Application | None:
        options = []
        if load_filled_fields:
            options.append(selectinload(ApplicationModel.filled_fields))
        if load_integrations:
            options.append(selectinload(ApplicationModel.integrations))
        if load_event_player:
            options.append(selectinload(ApplicationModel.event_player))

        return await self._get(field_id, options=options)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> Application | None:
        stmt = select(ApplicationModel).where(
            ApplicationModel.event_id == event_id,
            ApplicationModel.member_id == member_id,
        )
        obj = await self._session.scalar(stmt)

        return self._to_dto(obj) if obj else None

    async def list_by_event(
            self,
            event_id: UUID,
            offset: int = 0,
            limit: int = 100,
            status: ApplicationStatus | None = None,
            sort_by: str = "created_at",
            sort_order: str = "desc",
        load_event_player_with_roles: bool = False,
        load_integrations: bool = False,
    ) -> Sequence[Application]:
        where_clauses = [ApplicationModel.event_id == event_id]
        if status is not None:
            where_clauses.append(ApplicationModel.status == status)

        sort_column = getattr(ApplicationModel, sort_by, ApplicationModel.created_at)
        order_clause = sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc()

        options = []
        if load_event_player_with_roles:
            options.append(
                selectinload(ApplicationModel.event_player)
                .selectinload(EventPlayerModel.player_roles)
                .selectinload(PlayerRoleModel.game_role)
            )
        if load_integrations:
            options.append(selectinload(ApplicationModel.integrations))

        return await self.get_list(offset, limit, options, *where_clauses, order_by=order_clause)

    async def count_by_event_and_status(self, event_id: UUID, status: ApplicationStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(ApplicationModel)
            .where(ApplicationModel.event_id == event_id, ApplicationModel.status == status)
        )
        return (await self._session.scalar(stmt)) or 0
