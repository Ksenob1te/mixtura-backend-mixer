from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .application import Application
    from .event_player import EventPlayer
    from .team_player import TeamPlayer
    from .organizer import Organizer

class Member(Base):
    __tablename__ = 'member_table'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    applications: Mapped[list["Application"]] = relationship("Application", back_populates="member")
    event_players: Mapped[list["EventPlayer"]] = relationship("EventPlayer", back_populates="member")
    team_players: Mapped[list["TeamPlayer"]] = relationship("TeamPlayer", back_populates="member")
    organizers: Mapped[list["Organizer"]] = relationship("Organizer", back_populates="member")
