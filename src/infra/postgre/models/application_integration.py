from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .application import Application


class ApplicationIntegration(Base):
    """
    ApplicationIntegration table stores the integration of an application with external user providers.
    """
    __tablename__ = 'application_integration_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[UUID] = mapped_column(ForeignKey('application_table.id', ondelete="CASCADE"))
    user_provider_id: Mapped[UUID]

    application: Mapped["Application"] = relationship("Application", back_populates="integrations", lazy="raise")

    __table_args__ = (
        UniqueConstraint('application_id', 'user_provider_id', name='uq_app_integration_app_provider'),
    )
# TODO: А нам точно нужно тут вот такая табличка вообще, мы эти данные можем получить из сервиса авторизации
