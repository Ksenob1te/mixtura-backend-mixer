from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .stage import Stage

class RoundRobinSettings(Base):
    __tablename__ = 'round_robin_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id'), unique=True)
    meetings_per_pair: Mapped[int] = mapped_column(Integer)
    score_system: Mapped[str] = mapped_column(String)
    score_per_win: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_per_draw: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    stage: Mapped["Stage"] = relationship("Stage", back_populates="round_robin_settings", lazy="joined")
