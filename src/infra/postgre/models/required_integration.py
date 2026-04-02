from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel


class RequiredIntegrationModel(Base):
    """
    RequiredIntegration table stores integrations required for an event.
    """
    __tablename__ = 'required_integration_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="required_integrations", lazy="raise")
