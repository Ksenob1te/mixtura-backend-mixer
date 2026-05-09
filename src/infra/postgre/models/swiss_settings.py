import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .stage import StageModel


class SwissSettingsModel(Base):
    __tablename__ = 'swiss_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id', ondelete="CASCADE"), unique=True)
    score_per_win: Mapped[int] = mapped_column()
    score_per_draw: Mapped[int] = mapped_column()
    score_per_bye: Mapped[int] = mapped_column()

    stage: Mapped["StageModel"] = relationship("StageModel", back_populates="swiss_settings", lazy="noload")
