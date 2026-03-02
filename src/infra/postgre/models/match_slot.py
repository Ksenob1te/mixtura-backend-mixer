import enum
from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .match import Match
    from .stage_group import StageGroup
    from .match_score import MatchScore


class MatchSlotSourceType(str, enum.Enum):
    WINNER_OF = "WINNER_OF"
    LOSER_OF = "LOSER_OF"
    GROUP_PLACEMENT = "GROUP_PLACEMENT"
    MANUAL = "MANUAL"
    AUTO = "AUTO"


class MatchSlot(Base):
    """
    MatchSlot table represents a slot in a match, which can be filled by a team or another match result.
    """
    __tablename__ = 'match_slot_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_id: Mapped[UUID] = mapped_column(ForeignKey('match_table.id', ondelete="CASCADE"))
    slot_num: Mapped[int] = mapped_column()
    source_type: Mapped[MatchSlotSourceType] = mapped_column()
    source_match_id: Mapped[UUID | None] = mapped_column(ForeignKey('match_table.id', ondelete="SET NULL"),
                                                         nullable=True)
    source_group_id: Mapped[UUID | None] = mapped_column(ForeignKey('stage_group_table.id', ondelete="SET NULL"),
                                                         nullable=True)
    group_placement: Mapped[int | None] = mapped_column(nullable=True)

    match: Mapped["Match"] = relationship("Match", foreign_keys=[match_id], back_populates="slots", lazy="raise")
    source_match: Mapped["Match"] = relationship("Match", foreign_keys=[source_match_id], back_populates="source_slots",
                                                 lazy="raise")
    source_group: Mapped["StageGroup"] = relationship("StageGroup", back_populates="source_slots", lazy="raise")

    score: Mapped["MatchScore"] = relationship("MatchScore", back_populates="slot", uselist=False,
                                               cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        UniqueConstraint('match_id', 'slot_num', name='uq_match_slot_match_num'),
    )
