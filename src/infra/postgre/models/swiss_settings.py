from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .stage import Stage

class SwissSettings(Base):
    __tablename__ = 'swiss_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id'), unique=True)
    score_per_win: Mapped[int] = mapped_column(Integer)
    score_per_draw: Mapped[int] = mapped_column(Integer)
    score_per_bye: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    stage: Mapped["Stage"] = relationship("Stage", back_populates="swiss_settings", lazy="joined")
