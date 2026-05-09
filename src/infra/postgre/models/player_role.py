import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .selected_game_role import SelectedGameRoleModel
    from .event_player import EventPlayerModel


class PlayerRoleModel(Base):
    __tablename__ = 'player_role_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('selected_game_role_table.id', ondelete="CASCADE"))
    priority: Mapped[int] = mapped_column(default=0)
    event_player_id: Mapped[UUID] = mapped_column(ForeignKey('event_player_table.id', ondelete="CASCADE"))

    game_role: Mapped["SelectedGameRoleModel"] = relationship("SelectedGameRoleModel", back_populates="player_roles",
                                                              lazy="noload")
    event_player: Mapped["EventPlayerModel"] = relationship("EventPlayerModel", back_populates="player_roles",
                                                            lazy="noload")

    __table_args__ = (
        UniqueConstraint('game_role_id', 'event_player_id', name='uq_player_role_game_role_player'),
    )
