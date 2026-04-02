from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel


class ApplicationTimeSettingsModel(Base):
    """
    ApplicationTimeSettings table stores time configuration for event applications.
    """
    __tablename__ = 'application_time_settings_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"), unique=True)
    start_time: Mapped[datetime | None] = mapped_column(nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="time_settings", lazy="raise")
