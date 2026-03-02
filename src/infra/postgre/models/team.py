from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .draft import Draft
    from .team_player import TeamPlayer


class Team(Base):
    """
    Team table represents a team participating in an event.
    """
    __tablename__ = 'team_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    draft_id: Mapped[UUID | None] = mapped_column(ForeignKey('draft_table.id'), nullable=True)
    name: Mapped[str] = mapped_column()

    event: Mapped["Event"] = relationship("Event", back_populates="teams", lazy="raise")
    draft: Mapped["Draft"] = relationship("Draft", back_populates="teams", lazy="raise")

    players: Mapped[list["TeamPlayer"]] = relationship("TeamPlayer", back_populates="team",
                                                       cascade="all, delete-orphan", lazy="raise")
