from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundException
from src.core.interfaces.repo.team import TeamRepositoryProtocol
from src.core.models.team import Team, TeamCreate, TeamUpdate
from .base import BaseRepository
from ..models import TeamModel


class TeamRepository(BaseRepository[TeamModel, TeamCreate, Team, TeamUpdate], TeamRepositoryProtocol):
    model = TeamModel
    dto_model = Team

    async def get(
            self,
            field_id: UUID,
            load_event: bool = False,
            load_players: bool = False
    ) -> Team | None:
        options = []
        if load_event:
            options.append(selectinload(TeamModel.event))
        if load_players:
            options.append(selectinload(TeamModel.players))

        return await self._get(field_id, options=options)

    async def list_by_event(self, event_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Team]:
        return await self.get_list(
            offset, limit, None,
            TeamModel.event_id == event_id
        )

    async def update(self, dto: TeamUpdate) -> Team:  # type: ignore[override]
        obj = await self._get_model(dto.id)
        if not obj:
            raise NotFoundException("Team not found")
        update_data = self._dto_to_data(dto, exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self._flush()
        await self._session.refresh(obj)
        return self._to_dto(obj)
