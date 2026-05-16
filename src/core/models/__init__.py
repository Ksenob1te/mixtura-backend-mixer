from .application import Application, ApplicationCreate, ApplicationStatus, ApplicationUpdate
from .application_custom_field import (
    ApplicationCustomField,
    ApplicationCustomFieldCreate,
    ApplicationCustomFieldUpdate,
)
from .application_integration import ApplicationIntegration, ApplicationIntegrationCreate
from .application_time_settings import (
    ApplicationTimeSettings,
    ApplicationTimeSettingsCreate,
    ApplicationTimeSettingsUpdate,
)
from .bracket import Bracket, BracketCreate
from .bracket_placement import (
    BracketPlacement,
    BracketPlacementCreate,
    BracketPlacementUpdate,
)
from .draft import Draft, DraftCreate, DraftStatus, DraftUpdate
from .drafted_player import DraftedPlayer, DraftedPlayerCreate
from .event import (
    Event,
    EventCreate,
    EventMatchType,
    EventStatus,
    EventUpdate,
    TeamFormation,
)
from .event_player import (
    EventPlayer,
    EventPlayerCreate,
    EventPlayerStatus,
    EventPlayerUpdate,
)
from .filled_application_field import FilledApplicationField, FilledApplicationFieldCreate
from .match import BracketPosition, Match, MatchCreate, MatchUpdate
from .match_score import MatchScore, MatchScoreCreate, MatchScoreUpdate
from .match_slot import MatchSlot, MatchSlotCreate, MatchSlotSourceType
from .organizer import Organizer, OrganizerCreate
from .player_role import PlayerRole, PlayerRoleCreate, PlayerRoleUpdate
from .rating import (
    MatchPlayerInput,
    MatchTeamInput,
    PlayerEffectiveRating,
    RatingPlayerRequest,
    RatingSettings,
)
from .required_integration import (
    RequiredIntegration,
    RequiredIntegrationCreate,
    RequiredIntegrationUpdate,
)
from .round_robin_settings import (
    RoundRobinSettings,
    RoundRobinSettingsCreate,
    RoundRobinSettingsUpdate,
)
from .selected_game_role import (
    SelectedGameRole,
    SelectedGameRoleCreate,
    SelectedGameRoleUpdate,
)
from .stage import Stage, StageCreate, StageFormat, StageUpdate
from .stage_group import StageGroup, StageGroupCreate, StageGroupUpdate
from .swiss_settings import SwissSettings, SwissSettingsCreate, SwissSettingsUpdate
from .team import Team, TeamCreate, TeamUpdate
from .team_player import TeamPlayer, TeamPlayerCreate, TeamPlayerUpdate

__all__ = (
    "Application",
    "ApplicationCreate",
    "ApplicationCustomField",
    "ApplicationCustomFieldCreate",
    "ApplicationCustomFieldUpdate",
    "ApplicationIntegration",
    "ApplicationIntegrationCreate",
    "ApplicationStatus",
    "ApplicationTimeSettings",
    "ApplicationTimeSettingsCreate",
    "ApplicationTimeSettingsUpdate",
    "ApplicationUpdate",
    "Bracket",
    "BracketCreate",
    "BracketPlacement",
    "BracketPlacementCreate",
    "BracketPlacementUpdate",
    "BracketPosition",
    "Draft",
    "DraftCreate",
    "DraftStatus",
    "DraftUpdate",
    "DraftedPlayer",
    "DraftedPlayerCreate",
    "Event",
    "EventCreate",
    "EventMatchType",
    "EventPlayer",
    "EventPlayerCreate",
    "EventPlayerStatus",
    "EventPlayerUpdate",
    "EventStatus",
    "EventUpdate",
    "FilledApplicationField",
    "FilledApplicationFieldCreate",
    "Match",
    "MatchCreate",
    "MatchPlayerInput",
    "MatchScore",
    "MatchScoreCreate",
    "MatchScoreUpdate",
    "MatchSlot",
    "MatchSlotCreate",
    "MatchSlotSourceType",
    "MatchTeamInput",
    "MatchUpdate",
    "Organizer",
    "OrganizerCreate",
    "PlayerEffectiveRating",
    "PlayerRole",
    "PlayerRoleCreate",
    "PlayerRoleUpdate",
    "RatingPlayerRequest",
    "RatingSettings",
    "RequiredIntegration",
    "RequiredIntegrationCreate",
    "RequiredIntegrationUpdate",
    "RoundRobinSettings",
    "RoundRobinSettingsCreate",
    "RoundRobinSettingsUpdate",
    "SelectedGameRole",
    "SelectedGameRoleCreate",
    "SelectedGameRoleUpdate",
    "Stage",
    "StageCreate",
    "StageFormat",
    "StageGroup",
    "StageGroupCreate",
    "StageGroupUpdate",
    "StageUpdate",
    "SwissSettings",
    "SwissSettingsCreate",
    "SwissSettingsUpdate",
    "Team",
    "TeamCreate",
    "TeamFormation",
    "TeamPlayer",
    "TeamPlayerCreate",
    "TeamPlayerUpdate",
    "TeamUpdate",
)

_types_namespace = {name: globals()[name] for name in __all__}

for _model in _types_namespace.values():
    if hasattr(_model, "model_rebuild"):
        _model.model_rebuild(_types_namespace=_types_namespace)

del _types_namespace
