import enum
from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, Text, UniqueConstraint, Enum as AlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .stage_group import StageGroup
    from .match_slot import MatchSlot


class BracketPosition(str, enum.Enum):
    UPPER = "UPPER"
    LOWER = "LOWER"


class Match(Base):
    """
    Match table stores the match details within a stage group or bracket.
    """
    __tablename__ = 'match_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    group_id: Mapped[UUID | None] = mapped_column(ForeignKey('stage_group_table.id', ondelete="CASCADE"), nullable=True)
    match_index: Mapped[int | None] = mapped_column(nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    time_start: Mapped[datetime | None] = mapped_column(nullable=True)
    time_end: Mapped[datetime | None] = mapped_column(nullable=True)
    round_number: Mapped[int | None] = mapped_column(nullable=True)
    bracket_position: Mapped[BracketPosition | None] = mapped_column(nullable=True)

    group: Mapped["StageGroup"] = relationship("StageGroup", back_populates="matches", lazy="raise")
    slots: Mapped[list["MatchSlot"]] = relationship("MatchSlot", back_populates="match",
                                                    foreign_keys="MatchSlot.match_id",
                                                    cascade="all, delete-orphan", lazy="raise")
    source_slots: Mapped[list["MatchSlot"]] = relationship("MatchSlot", back_populates="source_match",
                                                           foreign_keys="MatchSlot.source_match_id", lazy="raise")

    __table_args__ = (
        UniqueConstraint('group_id', 'match_index', name='uq_match_group_index'),
    )
