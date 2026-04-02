from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .player_role import PlayerRoleModel
    from .team_player import TeamPlayerModel


class SelectedGameRoleModel(Base):
    """
    SelectedGameRole table stores the game roles selected for an event.
    """
    __tablename__ = 'selected_game_role_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_role_id: Mapped[UUID] = mapped_column()  # External reference
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    override_max_count: Mapped[int | None] = mapped_column(nullable=True)
    override_min_count: Mapped[int | None] = mapped_column(nullable=True)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="selected_game_roles", lazy="raise")

    player_roles: Mapped[list["PlayerRoleModel"]] = relationship("PlayerRoleModel", back_populates="game_role",
                                                            cascade="all, delete-orphan", lazy="raise")
    team_players: Mapped[list["TeamPlayerModel"]] = relationship("TeamPlayerModel", back_populates="game_role",
                                                            cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        UniqueConstraint('game_role_id', 'event_id', name='uq_selected_game_role_event'),
    )
