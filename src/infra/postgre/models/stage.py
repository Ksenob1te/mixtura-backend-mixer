from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

class Stage(Base):
    __tablename__ = 'stage_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_index: Mapped[int] = mapped_column(Integer)
    format: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    bracket_id: Mapped[UUID] = mapped_column(ForeignKey('bracket_table.id'))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    bracket: Mapped["Bracket"] = relationship("Bracket", back_populates="stages", lazy="joined")

    groups: Mapped[list["StageGroup"]] = relationship("StageGroup", back_populates="stage")
    round_robin_settings: Mapped["RoundRobinSettings"] = relationship("RoundRobinSettings", back_populates="stage", uselist=False)
    swiss_settings: Mapped["SwissSettings"] = relationship("SwissSettings", back_populates="stage", uselist=False)

    __table_args__ = (
        UniqueConstraint('bracket_id', 'stage_index', name='uq_stage_bracket_index'),
    )

if TYPE_CHECKING:
    from .bracket import Bracket
    from .stage_group import StageGroup
    from .round_robin_settings import RoundRobinSettings
    from .swiss_settings import SwissSettings
