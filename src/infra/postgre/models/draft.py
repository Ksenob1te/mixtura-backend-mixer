import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.draft import DraftStatus
from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .team import TeamModel
    from .drafted_player import DraftedPlayerModel


class DraftModel(Base):
    __tablename__ = 'draft_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    status: Mapped[DraftStatus] = mapped_column(default=DraftStatus.OPEN)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="drafts", lazy="raise")

    teams: Mapped[list["TeamModel"]] = relationship("TeamModel", back_populates="draft", lazy="raise")
    drafted_players: Mapped[list["DraftedPlayerModel"]] = relationship("DraftedPlayerModel", back_populates="draft",
                                                                       cascade="all, delete-orphan", lazy="raise")
