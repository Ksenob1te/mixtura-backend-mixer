from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .stage import Stage
    from .bracket_placement import BracketPlacement


class Bracket(Base):
    __tablename__ = 'bracket_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))

    event: Mapped["Event"] = relationship("Event", back_populates="brackets", lazy="raise")

    stages: Mapped[list["Stage"]] = relationship("Stage", back_populates="bracket")
    placements: Mapped[list["BracketPlacement"]] = relationship("BracketPlacement", back_populates="bracket")
