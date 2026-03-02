from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .stage import Stage
    from .bracket_placement import BracketPlacement


class Bracket(Base):
    """
    Bracket table represents a tournament bracket structure.
    """
    __tablename__ = 'bracket_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))

    event: Mapped["Event"] = relationship("Event", back_populates="brackets", lazy="raise")

    stages: Mapped[list["Stage"]] = relationship("Stage", back_populates="bracket", cascade="all, delete-orphan",
                                                 lazy="raise")
    placements: Mapped[list["BracketPlacement"]] = relationship("BracketPlacement", back_populates="bracket",
                                                                cascade="all, delete-orphan", lazy="raise")
