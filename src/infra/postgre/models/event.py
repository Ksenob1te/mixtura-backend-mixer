import enum
from typing import TYPE_CHECKING
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..engine import Base

if TYPE_CHECKING:
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


class EventStatus(str, enum.Enum):
    CREATED = "CREATED"
    REGISTRATION = "REGISTRATION"
    FORMATION = "FORMATION"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


EVENT_STATUS_TRANSITIONS = {
    EventStatus.CREATED: {EventStatus.REGISTRATION, EventStatus.CANCELLED},
    EventStatus.REGISTRATION: {EventStatus.FORMATION, EventStatus.CANCELLED},
    EventStatus.FORMATION: {EventStatus.IN_PROGRESS, EventStatus.REGISTRATION, EventStatus.CANCELLED},
    EventStatus.IN_PROGRESS: {EventStatus.COMPLETED, EventStatus.CANCELLED},
    EventStatus.COMPLETED: {EventStatus.IN_PROGRESS},  # Allow reopening if needed?
    EventStatus.CANCELLED: set(),
}


class Event(Base):
    """
    Event table stores the configuration and status of an event.
    """
    __tablename__ = 'event_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_type: Mapped[str] = mapped_column()
    use_application: Mapped[bool] = mapped_column(default=False)
    is_public: Mapped[bool] = mapped_column(default=False)
    team_size: Mapped[int] = mapped_column()
    registration_type: Mapped[str] = mapped_column()
    team_formation: Mapped[TeamFormation] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(default=EventStatus.CREATED)

    allow_multiple_drafts: Mapped[bool] = mapped_column(default=False)
    rating_set_id: Mapped[UUID | None] = mapped_column(nullable=True)

    applications: Mapped[list["Application"]] = relationship("Application", back_populates="event",
                                                             cascade="all, delete-orphan", lazy="raise")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="event", cascade="all, delete-orphan",
                                               lazy="raise")
    drafts: Mapped[list["Draft"]] = relationship("Draft", back_populates="event", cascade="all, delete-orphan",
                                                 lazy="raise")
    organizers: Mapped[list["Organizer"]] = relationship("Organizer", back_populates="event",
                                                         cascade="all, delete-orphan", lazy="raise")
    event_players: Mapped[list["EventPlayer"]] = relationship("EventPlayer", back_populates="event",
                                                              cascade="all, delete-orphan", lazy="raise")
    brackets: Mapped[list["Bracket"]] = relationship("Bracket", back_populates="event", cascade="all, delete-orphan",
                                                     lazy="raise")
    required_integrations: Mapped[list["RequiredIntegration"]] = relationship("RequiredIntegration",
                                                                              back_populates="event",
                                                                              cascade="all, delete-orphan",
                                                                              lazy="raise")
    selected_game_roles: Mapped[list["SelectedGameRole"]] = relationship("SelectedGameRole", back_populates="event",
                                                                         cascade="all, delete-orphan", lazy="raise")
    custom_fields: Mapped[list["ApplicationCustomField"]] = relationship("ApplicationCustomField",
                                                                         back_populates="event",
                                                                         cascade="all, delete-orphan", lazy="raise")
    time_settings: Mapped["ApplicationTimeSettings"] = relationship("ApplicationTimeSettings", back_populates="event",
                                                                    uselist=False, cascade="all, delete-orphan",
                                                                    lazy="raise")

    def validate_transition(self, new_status: EventStatus) -> None:
        allowed = EVENT_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid status transition: {self.status} -> {new_status}. Allowed: {allowed}"
            )

    def transition_to(self, new_status: EventStatus) -> None:
        if self.status == new_status:
            return
        self.validate_transition(new_status)
        self.status = new_status
