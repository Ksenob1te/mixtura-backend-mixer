from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .match_slot import MatchSlot
    from .team import Team


class MatchScore(Base):
    __tablename__ = 'match_score_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slot_id: Mapped[UUID] = mapped_column(ForeignKey('match_slot_table.id'), unique=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    score: Mapped[int] = mapped_column(Integer, default=0)

    slot: Mapped["MatchSlot"] = relationship("MatchSlot", back_populates="score", lazy="raise")
    team: Mapped["Team"] = relationship("Team", back_populates="match_scores", lazy="raise")

    # TODO: STOPPED HERE