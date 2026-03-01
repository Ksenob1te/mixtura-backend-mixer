from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

class Team(Base):
    __tablename__ = 'team_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id'))
    draft_id: Mapped[UUID | None] = mapped_column(ForeignKey('draft_table.id'), nullable=True)
    name: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    event: Mapped["Event"] = relationship("Event", back_populates="teams", lazy="joined")
    draft: Mapped["Draft"] = relationship("Draft", back_populates="teams", lazy="joined")

    players: Mapped[list["TeamPlayer"]] = relationship("TeamPlayer", back_populates="team")
    match_scores: Mapped[list["MatchScore"]] = relationship("MatchScore", back_populates="team")
    bracket_placements: Mapped[list["BracketPlacement"]] = relationship("BracketPlacement", back_populates="team")

if TYPE_CHECKING:
    from .event import Event
    from .draft import Draft
    from .team_player import TeamPlayer
    from .match_score import MatchScore
    from .bracket_placement import BracketPlacement
