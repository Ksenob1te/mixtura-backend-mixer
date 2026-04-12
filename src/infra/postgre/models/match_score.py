import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .match_slot import MatchSlotModel
    from .team import TeamModel


class MatchScoreModel(Base):
    __tablename__ = 'match_score_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slot_id: Mapped[UUID] = mapped_column(ForeignKey('match_slot_table.id', ondelete="CASCADE"), unique=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id', ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(default=0)

    slot: Mapped["MatchSlotModel"] = relationship("MatchSlotModel", back_populates="score", lazy="raise")
    team: Mapped["TeamModel"] = relationship("TeamModel", back_populates="match_scores", lazy="raise")
