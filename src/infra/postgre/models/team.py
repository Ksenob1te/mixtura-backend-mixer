import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..engine import Base

if TYPE_CHECKING:
    from .event import EventModel
    from .draft import DraftModel
    from .bracket_placement import BracketPlacementModel
    from .match_score import MatchScoreModel
    from .team_player import TeamPlayerModel


class TeamModel(Base):
    __tablename__ = 'team_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('event_table.id', ondelete="CASCADE"))
    draft_id: Mapped[UUID | None] = mapped_column(ForeignKey('draft_table.id'), nullable=True)
    name: Mapped[str] = mapped_column()

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="teams", lazy="noload")
    draft: Mapped["DraftModel"] = relationship("DraftModel", back_populates="teams", lazy="noload")

    players: Mapped[list["TeamPlayerModel"]] = relationship("TeamPlayerModel", back_populates="team",
                                                            cascade="all, delete-orphan", lazy="noload")
    bracket_placements: Mapped[list["BracketPlacementModel"]] = relationship(
        "BracketPlacementModel", back_populates="team", lazy="noload"
    )
    match_scores: Mapped[list["MatchScoreModel"]] = relationship("MatchScoreModel", back_populates="team",
                                                                 lazy="noload")
