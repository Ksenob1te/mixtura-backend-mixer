import enum
from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, Text, CheckConstraint, UniqueConstraint, Enum as AlchemyEnum
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
    __tablename__ = 'match_slot_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_id: Mapped[UUID] = mapped_column(ForeignKey('match_table.id'))
    slot_num: Mapped[int] = mapped_column(Integer)
    source_type: Mapped[MatchSlotSourceType] = mapped_column(AlchemyEnum(MatchSlotSourceType))
    source_match_id: Mapped[UUID | None] = mapped_column(ForeignKey('match_table.id'), nullable=True)
    source_group_id: Mapped[UUID | None] = mapped_column(ForeignKey('stage_group_table.id'), nullable=True)
    group_placement: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    match: Mapped["Match"] = relationship("Match", foreign_keys=[match_id], back_populates="slots", lazy="joined")
    source_match: Mapped["Match"] = relationship("Match", foreign_keys=[source_match_id], back_populates="source_slots", lazy="joined")
    source_group: Mapped["StageGroup"] = relationship("StageGroup", back_populates="source_slots", lazy="joined")

    score: Mapped["MatchScore"] = relationship("MatchScore", back_populates="slot", uselist=False)

    __table_args__ = (
        UniqueConstraint('match_id', 'slot_num', name='uq_match_slot_match_num'),
    )


