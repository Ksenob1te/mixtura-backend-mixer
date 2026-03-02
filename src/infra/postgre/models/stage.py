from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .bracket import Bracket
    from .stage_group import StageGroup
    from .round_robin_settings import RoundRobinSettings
    from .swiss_settings import SwissSettings


class Stage(Base):
    """
    Stage table represents a competitive stage within a bracket.
    """
    __tablename__ = 'stage_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_index: Mapped[int] = mapped_column()
    format: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    bracket_id: Mapped[UUID] = mapped_column(ForeignKey('bracket_table.id', ondelete="CASCADE"))

    bracket: Mapped["Bracket"] = relationship("Bracket", back_populates="stages", lazy="raise")

    groups: Mapped[list["StageGroup"]] = relationship("StageGroup", back_populates="stage",
                                                      cascade="all, delete-orphan", lazy="raise")
    round_robin_settings: Mapped["RoundRobinSettings"] = relationship("RoundRobinSettings", back_populates="stage",
                                                                      uselist=False, cascade="all, delete-orphan",
                                                                      lazy="raise")
    swiss_settings: Mapped["SwissSettings"] = relationship("SwissSettings", back_populates="stage", uselist=False,
                                                           cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        UniqueConstraint('bracket_id', 'stage_index', name='uq_stage_bracket_index'),
    )
