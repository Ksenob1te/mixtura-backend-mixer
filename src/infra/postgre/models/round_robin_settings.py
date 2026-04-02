from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .stage import StageModel


class RoundRobinSettingsModel(Base):
    """
    RoundRobinSettings table stores configuration for round-robin stages.
    """
    __tablename__ = 'round_robin_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id', ondelete="CASCADE"), unique=True)
    meetings_per_pair: Mapped[int] = mapped_column()
    score_system: Mapped[str] = mapped_column()
    score_per_win: Mapped[int | None] = mapped_column(nullable=True)
    score_per_draw: Mapped[int | None] = mapped_column(nullable=True)

    stage: Mapped["StageModel"] = relationship("StageModel", back_populates="round_robin_settings", lazy="raise")
