from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .stage import Stage

class StageGroup(Base):
    __tablename__ = 'stage_group_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id'))
    name: Mapped[str] = mapped_column(String)
    advance_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    stage: Mapped["Stage"] = relationship("Stage", back_populates="groups", lazy="joined")

    matches: Mapped[list["Match"]] = relationship("Match", back_populates="group")
    source_slots: Mapped[list["MatchSlot"]] = relationship("MatchSlot", back_populates="source_group")

if TYPE_CHECKING:
    from .match import Match
    from .match_slot import MatchSlot
