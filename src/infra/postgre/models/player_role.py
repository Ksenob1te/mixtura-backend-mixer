from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .selected_game_role import SelectedGameRole
    from .event_player import EventPlayer


class PlayerRole(Base):
    """
    PlayerRole table stores the preferred roles of a player in an event.
    """
    __tablename__ = 'player_role_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('selected_game_role_table.id', ondelete="CASCADE"))
    priority: Mapped[int] = mapped_column(default=0)
    event_player_id: Mapped[UUID] = mapped_column(ForeignKey('event_player_table.id', ondelete="CASCADE"))

    game_role: Mapped["SelectedGameRole"] = relationship("SelectedGameRole", back_populates="player_roles",
                                                         lazy="raise")
    event_player: Mapped["EventPlayer"] = relationship("EventPlayer", back_populates="player_roles", lazy="raise")

    __table_args__ = (
        UniqueConstraint('game_role_id', 'event_player_id', name='uq_player_role_game_role_player'),
    )
