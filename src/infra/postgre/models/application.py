import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.application import ApplicationStatus
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .application_integration import ApplicationIntegrationModel
    from .filled_application_field import FilledApplicationFieldModel
    from .event_player import EventPlayerModel


class ApplicationModel(Base):
    __tablename__ = 'application_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    member_id: Mapped[UUID]
    status: Mapped[ApplicationStatus] = mapped_column(default=ApplicationStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="applications", lazy="noload")

    integrations: Mapped[list["ApplicationIntegrationModel"]] = relationship("ApplicationIntegrationModel",
                                                                             back_populates="application",
                                                                             cascade="all, delete-orphan", lazy="noload")
    filled_fields: Mapped[list["FilledApplicationFieldModel"]] = relationship("FilledApplicationFieldModel",
                                                                              back_populates="application",
                                                                              cascade="all, delete-orphan",
                                                                              lazy="noload")
    event_player: Mapped["EventPlayerModel"] = relationship("EventPlayerModel", back_populates="application",
                                                            uselist=False,
                                                            lazy="noload")

    __table_args__ = (
        UniqueConstraint('event_id', 'member_id', name='uq_application_event_member'),
    )
