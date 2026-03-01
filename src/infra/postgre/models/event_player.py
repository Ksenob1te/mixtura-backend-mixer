from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .member import Member
    from .application import Application
    from .drafted_player import DraftedPlayer
    from .player_role import PlayerRole


class EventPlayer(Base):
    __tablename__ = 'event_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))
    member_id: Mapped[UUID] = mapped_column(ForeignKey('member_table.id'))
    application_id: Mapped[UUID | None] = mapped_column(ForeignKey('application_table.id'), nullable=True)
    custom_id: Mapped[UUID | None] = mapped_column(nullable=True)
    is_draft_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    event: Mapped["Event"] = relationship("Event", back_populates="event_players", lazy="joined")
    member: Mapped["Member"] = relationship("Member", back_populates="event_players", lazy="joined")
    application: Mapped["Application"] = relationship("Application", back_populates="event_player", lazy="joined")

    drafted_players: Mapped[list["DraftedPlayer"]] = relationship("DraftedPlayer", back_populates="event_player")
    player_roles: Mapped[list["PlayerRole"]] = relationship("PlayerRole", back_populates="event_player")

    __table_args__ = (
        UniqueConstraint('event_id', 'member_id', name='uq_event_player_member'),
    )
    # TODO: custom_id or application_id always null?

