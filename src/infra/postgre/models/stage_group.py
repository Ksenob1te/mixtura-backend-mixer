from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
    from .stage import StageModel
    from .match import MatchModel


class StageGroupModel(Base):
    """
    StageGroup table represents a group of teams within a stage.
    """
    __tablename__ = 'stage_group_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[UUID] = mapped_column(ForeignKey('stage_table.id', ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    advance_count: Mapped[int | None] = mapped_column(nullable=True) # TODO: что это

    stage: Mapped["StageModel"] = relationship("StageModel", back_populates="groups", lazy="raise")

    matches: Mapped[list["MatchModel"]] = relationship("MatchModel", back_populates="group",
                                                  cascade="all, delete-orphan", lazy="raise")
