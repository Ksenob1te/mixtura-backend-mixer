from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

class SelectedGameRole(Base):
    __tablename__ = 'selected_game_role_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_role_id: Mapped[UUID] = mapped_column(ForeignKey('game_role_table.id'))
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))
    override_max_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    override_min_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    game_role: Mapped["GameRole"] = relationship("GameRole", lazy="joined")
    event: Mapped["Event"] = relationship("Event", back_populates="selected_game_roles", lazy="joined")

    player_roles: Mapped[list["PlayerRole"]] = relationship("PlayerRole", back_populates="game_role")
    team_players: Mapped[list["TeamPlayer"]] = relationship("TeamPlayer", back_populates="game_role")

    __table_args__ = (
        UniqueConstraint('game_role_id', 'event_id', name='uq_selected_game_role_event'),
    )

if TYPE_CHECKING:
    from .game_role import GameRole
    from .event import Event
    from .player_role import PlayerRole
    from .team_player import TeamPlayer
