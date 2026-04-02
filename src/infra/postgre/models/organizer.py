from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel


class OrganizerModel(Base):
    """
    Organizer table stores the organizers of an event.
    """
    __tablename__ = 'organizer_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    member_id: Mapped[UUID]

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="organizers", lazy="raise")

    # __table_args__ = (
    #     UniqueConstraint('event_id', 'member_id', name='uq_organizer_event_member'),
    # )
