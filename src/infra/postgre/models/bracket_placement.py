from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .bracket import Bracket
    from .team import Team


class BracketPlacement(Base):
    """
    BracketPlacement table stores the initial placement of teams in a bracket.
    """
    __tablename__ = 'bracket_placement_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bracket_id: Mapped[UUID] = mapped_column(ForeignKey('bracket_table.id', ondelete="CASCADE"))
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    placement: Mapped[int] = mapped_column()

    bracket: Mapped["Bracket"] = relationship("Bracket", back_populates="placements", lazy="raise")
    team: Mapped["Team"] = relationship("Team", back_populates="bracket_placements", lazy="raise")

    __table_args__ = (
        UniqueConstraint('bracket_id', 'placement', name='uq_bracket_placement_placement'),
        UniqueConstraint('bracket_id', 'team_id', name='uq_bracket_placement_team'),
    )
