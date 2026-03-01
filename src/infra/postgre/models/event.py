import enum
from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, func, Enum as AlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.postgre.engine import Base

if TYPE_CHECKING:
    from .rating_set import RatingSet
    from .application import Application
    from .team import Team
    from .draft import Draft
    from .organizer import Organizer
    from .event_player import EventPlayer
    from .bracket import Bracket
    from .required_integration import RequiredIntegration
    from .selected_game_role import SelectedGameRole
    from .application_custom_field import ApplicationCustomField
    from .application_time_settings import ApplicationTimeSettings


class TeamFormation(str, enum.Enum):
    DRAFT = "DRAFT"
    BALANCE = "BALANCE"
    MANUAL = "MANUAL"


class Event(Base):
    __tablename__ = 'event_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_type: Mapped[str] = mapped_column(String)
    use_application: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    team_size: Mapped[int] = mapped_column(Integer)
    registration_type: Mapped[str] = mapped_column(String)
    team_formation: Mapped[TeamFormation] = mapped_column(AlchemyEnum(TeamFormation))
    allow_multiple_drafts: Mapped[bool] = mapped_column(Boolean, default=False)
    rating_set_id: Mapped[UUID | None] = mapped_column(ForeignKey('rating_set_table.id'), nullable=True)

    rating_set: Mapped["RatingSet"] = relationship("RatingSet", lazy="raise")

    applications: Mapped[list["Application"]] = relationship("Application", back_populates="event", lazy="raise")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="event", lazy="raise")
    drafts: Mapped[list["Draft"]] = relationship("Draft", back_populates="event", lazy="raise")
    organizers: Mapped[list["Organizer"]] = relationship("Organizer", back_populates="event", lazy="raise")
    event_players: Mapped[list["EventPlayer"]] = relationship("EventPlayer", back_populates="event", lazy="raise")
    brackets: Mapped[list["Bracket"]] = relationship("Bracket", back_populates="event", lazy="raise")
    required_integrations: Mapped[list["RequiredIntegration"]] = relationship("RequiredIntegration",
                                                                              back_populates="event", lazy="raise")
    selected_game_roles: Mapped[list["SelectedGameRole"]] = relationship("SelectedGameRole", back_populates="event",
                                                                         lazy="raise")
    custom_fields: Mapped[list["ApplicationCustomField"]] = relationship("ApplicationCustomField",
                                                                         back_populates="event", lazy="raise")
    time_settings: Mapped["ApplicationTimeSettings"] = relationship("ApplicationTimeSettings", back_populates="event",
                                                                    uselist=False, lazy="raise")
