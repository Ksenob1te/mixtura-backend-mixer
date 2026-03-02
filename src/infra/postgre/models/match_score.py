from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .match_slot import MatchSlot
    from .team import Team


class MatchScore(Base):
    """
    MatchScore table stores the score of a team in a match slot.
    """
    __tablename__ = 'match_score_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slot_id: Mapped[UUID] = mapped_column(ForeignKey('match_slot_table.id', ondelete="CASCADE"), unique=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id', ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(default=0)

    slot: Mapped["MatchSlot"] = relationship("MatchSlot", back_populates="score", lazy="raise")
    team: Mapped["Team"] = relationship("Team", back_populates="match_scores", lazy="raise")
