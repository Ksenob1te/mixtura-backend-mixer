from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .draft import Draft
    from .event_player import EventPlayer


class DraftedPlayer(Base):
    __tablename__ = 'drafted_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey('draft_table.id'))
    event_player_id: Mapped[UUID] = mapped_column(ForeignKey('event_player_table.id'))
    is_captain: Mapped[bool | None] = mapped_column(Boolean, default=None, nullable=True)

    draft: Mapped["Draft"] = relationship("Draft", back_populates="drafted_players", lazy="raise")
    event_player: Mapped["EventPlayer"] = relationship("EventPlayer", back_populates="drafted_players", lazy="raise")

    __table_args__ = (
        UniqueConstraint('draft_id', 'event_player_id', name='uq_drafted_player_draft_player'),
    )
