from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .application_custom_field import ApplicationCustomField
    from .application import Application


class FilledApplicationField(Base):
    """
    FilledApplicationField table stores the values provided by users for custom application fields.
    """
    __tablename__ = 'filled_application_field_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    value: Mapped[str] = mapped_column(Text)
    custom_field_id: Mapped[UUID] = mapped_column(ForeignKey('application_custom_field_table.id'))
    application_id: Mapped[UUID] = mapped_column(ForeignKey('application_table.id', ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    custom_field: Mapped["ApplicationCustomField"] = relationship("ApplicationCustomField",
                                                                  back_populates="filled_fields", lazy="raise")
    application: Mapped["Application"] = relationship("Application", back_populates="filled_fields", lazy="raise")

    __table_args__ = (
        UniqueConstraint('custom_field_id', 'application_id', name='uq_filled_app_field_custom_app'),
    )
