from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .stage import Stage


class SwissSettings(Base):
    """
    SwissSettings table stores configuration for swiss system stages.
    """
    __tablename__ = 'swiss_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id', ondelete="CASCADE"), unique=True)
    score_per_win: Mapped[int] = mapped_column()
    score_per_draw: Mapped[int] = mapped_column()
    score_per_bye: Mapped[int] = mapped_column()

    stage: Mapped["Stage"] = relationship("Stage", back_populates="swiss_settings", lazy="raise")
