from typing import TYPE_CHECKING
import enum
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .team import Team
    from .drafted_player import DraftedPlayer


class DraftStatus(str, enum.Enum):
    OPEN = 'OPEN'
    BALANCE_REQUESTED = 'BALANCE_REQUESTED'
    BALANCE_SELECTED = 'BALANCE_SELECTED'
    COMPLETED = 'COMPLETED'


class Draft(Base):
    """
    Draft table stores the draft sessions for an event.
    """
    __tablename__ = 'draft_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    status: Mapped[DraftStatus] = mapped_column(default=DraftStatus.OPEN)

    event: Mapped["Event"] = relationship("Event", back_populates="drafts", lazy="raise")

    teams: Mapped[list["Team"]] = relationship("Team", back_populates="draft", lazy="raise")
    drafted_players: Mapped[list["DraftedPlayer"]] = relationship("DraftedPlayer", back_populates="draft",
                                                                  cascade="all, delete-orphan", lazy="raise")
