import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .application_custom_field import ApplicationCustomFieldModel
    from .application import ApplicationModel


class FilledApplicationFieldModel(Base):
    __tablename__ = 'filled_application_field_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    value: Mapped[str] = mapped_column(Text)
    custom_field_id: Mapped[UUID] = mapped_column(ForeignKey('application_custom_field_table.id'))
    application_id: Mapped[UUID] = mapped_column(ForeignKey('application_table.id', ondelete="CASCADE"))

    custom_field: Mapped["ApplicationCustomFieldModel"] = relationship("ApplicationCustomFieldModel",
                                                                       back_populates="filled_fields", lazy="noload")
    application: Mapped["ApplicationModel"] = relationship("ApplicationModel", back_populates="filled_fields",
                                                           lazy="noload")

    __table_args__ = (
        UniqueConstraint('custom_field_id', 'application_id', name='uq_filled_app_field_custom_app'),
    )
