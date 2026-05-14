import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel


class RequiredIntegrationModel(Base):
    __tablename__ = 'required_integration_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[UUID]
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="required_integrations", lazy="noload")

    __table_args__ = (
        UniqueConstraint('event_id', 'provider_id', name='uq_required_integration_event_provider'),
    )
