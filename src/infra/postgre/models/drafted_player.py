import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .draft import DraftModel
    from .event_player import EventPlayerModel


class DraftedPlayerModel(Base):
    __tablename__ = 'drafted_player_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey('draft_table.id', ondelete="CASCADE"))
    event_player_id: Mapped[UUID] = mapped_column(ForeignKey('event_player_table.id', ondelete="CASCADE"))
    is_captain: Mapped[bool | None] = mapped_column(default=None, nullable=True)

    draft: Mapped["DraftModel"] = relationship("DraftModel", back_populates="drafted_players", lazy="noload")
    event_player: Mapped["EventPlayerModel"] = relationship("EventPlayerModel", back_populates="drafted_players",
                                                            lazy="noload")

    __table_args__ = (
        UniqueConstraint('draft_id', 'event_player_id', name='uq_drafted_player_draft_player'),
    )
