from typing import TYPE_CHECKING
import enum
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Boolean, UniqueConstraint, Enum as AlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .member import Member
    from .application_integration import ApplicationIntegration
    from .filled_application_field import FilledApplicationField
    from .event_player import EventPlayer


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WAITLIST = "WAITLIST"


class Application(Base):
    __tablename__ = 'application_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))
    member_id: Mapped[UUID] = mapped_column(ForeignKey('member_table.id'))
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[ApplicationStatus] = mapped_column(AlchemyEnum(ApplicationStatus), default=ApplicationStatus.PENDING)

    event: Mapped["Event"] = relationship("Event", back_populates="applications", lazy="raise")
    member: Mapped["Member"] = relationship("Member", back_populates="applications", lazy="raise")

    integrations: Mapped[list["ApplicationIntegration"]] = relationship("ApplicationIntegration",
                                                                        back_populates="application")
    filled_fields: Mapped[list["FilledApplicationField"]] = relationship("FilledApplicationField",
                                                                         back_populates="application")
    event_player: Mapped["EventPlayer"] = relationship("EventPlayer", back_populates="application", uselist=False)

    __table_args__ = (
        UniqueConstraint('event_id', 'member_id', name='uq_application_event_member'),
    )
