from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .event import Event
    from .member import Member

class Organizer(Base):
    __tablename__ = 'organizer_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))
    member_id: Mapped[UUID] = mapped_column(ForeignKey('member_table.id'))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    event: Mapped["Event"] = relationship("Event", back_populates="organizers", lazy="joined")
    member: Mapped["Member"] = relationship("Member", back_populates="organizers", lazy="joined")

    __table_args__ = (
        UniqueConstraint('event_id', 'member_id', name='uq_organizer_event_member'),
    )
