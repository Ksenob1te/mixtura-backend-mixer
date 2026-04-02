from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel


class ApplicationCustomFieldModel(Base):
    """
    ApplicationCustomField table stores custom fields defined for an event application.
    """
    __tablename__ = 'application_custom_field_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    is_private: Mapped[bool] = mapped_column(default=False)
    is_required: Mapped[bool] = mapped_column(default=False)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="custom_fields", lazy="raise")
