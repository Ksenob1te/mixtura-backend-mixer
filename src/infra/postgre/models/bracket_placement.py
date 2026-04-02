from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .bracket import BracketModel
    from .team import TeamModel


class BracketPlacementModel(Base):
    """
    BracketPlacement table stores the initial placement of teams in a bracket.
    """
    __tablename__ = 'bracket_placement_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bracket_id: Mapped[UUID] = mapped_column(ForeignKey('bracket_table.id', ondelete="CASCADE"))
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    placement: Mapped[int] = mapped_column()

    bracket: Mapped["BracketModel"] = relationship("BracketModel", back_populates="placements", lazy="raise")
    team: Mapped["TeamModel"] = relationship("TeamModel", back_populates="bracket_placements", lazy="raise")

    __table_args__ = (
        UniqueConstraint('bracket_id', 'placement', name='uq_bracket_placement_placement'),
        UniqueConstraint('bracket_id', 'team_id', name='uq_bracket_placement_team'),
    )
