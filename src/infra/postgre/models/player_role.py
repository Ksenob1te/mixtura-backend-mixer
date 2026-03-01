from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .selected_game_role import SelectedGameRole
    from .event_player import EventPlayer

class PlayerRole(Base):
    __tablename__ = 'player_role_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('selected_game_role_table.id'))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    event_player_id: Mapped[UUID] = mapped_column(ForeignKey('event_player_table.id'))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    game_role: Mapped["SelectedGameRole"] = relationship("SelectedGameRole", back_populates="player_roles", lazy="joined")
    event_player: Mapped["EventPlayer"] = relationship("EventPlayer", back_populates="player_roles", lazy="joined")

    __table_args__ = (
        UniqueConstraint('game_role_id', 'event_player_id', name='uq_player_role_game_role_player'),
    )
