from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .application import ApplicationModel
    from .drafted_player import DraftedPlayerModel
    from .player_role import PlayerRoleModel


class EventPlayerModel(Base):
    """
    EventPlayer table stores the players registered for an event.
    """
    __tablename__ = 'event_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    member_id: Mapped[UUID] = mapped_column()  # External reference
    application_id: Mapped[UUID | None] = mapped_column(ForeignKey('application_table.id'), nullable=True)
    custom_id: Mapped[UUID | None] = mapped_column(nullable=True)
    is_draft_pinned: Mapped[bool] = mapped_column(default=False)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="event_players", lazy="raise")
    application: Mapped["ApplicationModel"] = relationship("ApplicationModel", back_populates="event_player", lazy="raise")

    drafted_players: Mapped[list["DraftedPlayerModel"]] = relationship("DraftedPlayerModel", back_populates="event_player",
                                                                  cascade="all, delete-orphan", lazy="raise")
    player_roles: Mapped[list["PlayerRoleModel"]] = relationship("PlayerRoleModel", back_populates="event_player",
                                                            cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        UniqueConstraint('event_id', 'member_id', name='uq_event_player_member'),
    )
    # TODO: custom_id or application_id always null?
