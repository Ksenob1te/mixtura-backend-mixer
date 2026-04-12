import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.match_slot import MatchSlotSourceType
from ..engine import Base

if TYPE_CHECKING:
    from .match import MatchModel
    from .stage_group import StageGroupModel
    from .match_score import MatchScoreModel


class MatchSlotModel(Base):
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

    match: Mapped["MatchModel"] = relationship("MatchModel", foreign_keys=[match_id], back_populates="slots",
                                               lazy="raise")
    source_match: Mapped["MatchModel"] = relationship("MatchModel", foreign_keys=[source_match_id],
                                                      back_populates="source_slots",
                                                      lazy="raise")
    source_group: Mapped["StageGroupModel"] = relationship("StageGroupModel", back_populates="source_slots",
                                                           lazy="raise")

    score: Mapped["MatchScoreModel"] = relationship("MatchScoreModel", back_populates="slot", uselist=False,
                                                    cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        UniqueConstraint('match_id', 'slot_num', name='uq_match_slot_match_num'),
    )
