import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.event import EventStatus, TeamFormation
from src.env_config import env
from ..engine import Base

if TYPE_CHECKING:
    from .application import ApplicationModel
    from .team import TeamModel
    from .draft import DraftModel
    from .organizer import OrganizerModel
    from .event_player import EventPlayerModel
    from .bracket import BracketModel
    from .required_integration import RequiredIntegrationModel
    from .selected_game_role import SelectedGameRoleModel
    from .application_custom_field import ApplicationCustomFieldModel
    from .application_time_settings import ApplicationTimeSettingsModel

EVENT_STATUS_TRANSITIONS = env.event_flow.get_transitions(EventStatus)


class EventModel(Base):
    __tablename__ = 'event_table'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_type: Mapped[str] = mapped_column()
    use_application: Mapped[bool] = mapped_column(default=False)
    is_public: Mapped[bool] = mapped_column(default=False)
    team_size: Mapped[int] = mapped_column()
    registration_type: Mapped[str] = mapped_column()
    team_formation: Mapped[TeamFormation] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(default=EventStatus.CREATED)  # type: ignore

    allow_multiple_drafts: Mapped[bool] = mapped_column(default=False)
    rating_set_id: Mapped[UUID | None] = mapped_column(nullable=True)

    applications: Mapped[list["ApplicationModel"]] = relationship("ApplicationModel", back_populates="event",
                                                                  cascade="all, delete-orphan", lazy="raise")
    teams: Mapped[list["TeamModel"]] = relationship("TeamModel", back_populates="event", cascade="all, delete-orphan",
                                                    lazy="raise")
    drafts: Mapped[list["DraftModel"]] = relationship("DraftModel", back_populates="event",
                                                      cascade="all, delete-orphan",
                                                      lazy="raise")
    organizers: Mapped[list["OrganizerModel"]] = relationship("OrganizerModel", back_populates="event",
                                                              cascade="all, delete-orphan", lazy="raise")
    event_players: Mapped[list["EventPlayerModel"]] = relationship("EventPlayerModel", back_populates="event",
                                                                   cascade="all, delete-orphan", lazy="raise")
    brackets: Mapped[list["BracketModel"]] = relationship("BracketModel", back_populates="event",
                                                          cascade="all, delete-orphan",
                                                          lazy="raise")
    required_integrations: Mapped[list["RequiredIntegrationModel"]] = relationship("RequiredIntegrationModel",
                                                                                   back_populates="event",
                                                                                   cascade="all, delete-orphan",
                                                                                   lazy="raise")
    selected_game_roles: Mapped[list["SelectedGameRoleModel"]] = relationship("SelectedGameRoleModel",
                                                                              back_populates="event",
                                                                              cascade="all, delete-orphan",
                                                                              lazy="raise")
    custom_fields: Mapped[list["ApplicationCustomFieldModel"]] = relationship("ApplicationCustomFieldModel",
                                                                              back_populates="event",
                                                                              cascade="all, delete-orphan",
                                                                              lazy="raise")
    time_settings: Mapped["ApplicationTimeSettingsModel"] = relationship("ApplicationTimeSettingsModel",
                                                                         back_populates="event",
                                                                         uselist=False, cascade="all, delete-orphan",
                                                                         lazy="raise")

    def _validate_transition(self, new_status: EventStatus) -> None:  # type: ignore
        if not EVENT_STATUS_TRANSITIONS:
            raise ValueError("Event table must contain a transition table")
        allowed = EVENT_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid status transition: {self.status} -> {new_status}. Allowed: {allowed}"
            )

    def transition_to(self, new_status: EventStatus) -> None:
        if self.status == new_status:
            return
        self._validate_transition(new_status)
        self.status = new_status
