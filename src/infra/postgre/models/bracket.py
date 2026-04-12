import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .stage import StageModel
    from .bracket_placement import BracketPlacementModel


class BracketModel(Base):
    __tablename__ = 'bracket_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="brackets", lazy="raise")

    stages: Mapped[list["StageModel"]] = relationship("StageModel", back_populates="bracket",
                                                      cascade="all, delete-orphan",
                                                      lazy="raise")
    placements: Mapped[list["BracketPlacementModel"]] = relationship("BracketPlacementModel", back_populates="bracket",
                                                                     cascade="all, delete-orphan", lazy="raise")
