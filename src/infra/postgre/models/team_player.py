from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .team import Team
    from .selected_game_role import SelectedGameRole


class TeamPlayer(Base):
    """
    TeamPlayer table stores the players assigned to a team.
    """
    __tablename__ = 'team_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    member_id: Mapped[UUID] = mapped_column()  # External reference
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('selected_game_role_table.id'))
    rating: Mapped[float] = mapped_column(default=0.0)

    team: Mapped["Team"] = relationship("Team", back_populates="players", lazy="raise")
    game_role: Mapped["SelectedGameRole"] = relationship("SelectedGameRole", back_populates="team_players",
                                                         lazy="raise")

    __table_args__ = (
        UniqueConstraint('team_id', 'member_id', name='uq_team_player_team_member'),
    )
