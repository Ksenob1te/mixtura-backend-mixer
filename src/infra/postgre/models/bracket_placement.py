from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .bracket import Bracket
    from .team import Team


class BracketPlacement(Base):
    __tablename__ = 'bracket_placement_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bracket_id: Mapped[UUID] = mapped_column(ForeignKey('bracket_table.id'))
    team_id: Mapped[UUID] = mapped_column(ForeignKey('team_table.id'))
    placement: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    bracket: Mapped["Bracket"] = relationship("Bracket", back_populates="placements", lazy="raise")
    team: Mapped["Team"] = relationship("Team", back_populates="bracket_placements", lazy="raise")

    __table_args__ = (
        UniqueConstraint('bracket_id', 'placement', name='uq_bracket_placement_placement'),
        UniqueConstraint('bracket_id', 'team_id', name='uq_bracket_placement_team'),
    )
