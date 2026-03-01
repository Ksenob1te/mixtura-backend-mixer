from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .team import Team
    from .member import Member
    from .selected_game_role import SelectedGameRole

class TeamPlayer(Base):
    __tablename__ = 'team_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    member_id: Mapped[UUID] = mapped_column(ForeignKey('member_table.id'))
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('selected_game_role_table.id'))
    rating: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    team: Mapped["Team"] = relationship("Team", back_populates="players", lazy="joined")
    member: Mapped["Member"] = relationship("Member", back_populates="team_players", lazy="joined")
    game_role: Mapped["SelectedGameRole"] = relationship("SelectedGameRole", back_populates="team_players", lazy="joined")

    __table_args__ = (
        UniqueConstraint('team_id', 'member_id', name='uq_team_player_team_member'),
    )
