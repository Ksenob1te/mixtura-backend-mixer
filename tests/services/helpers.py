from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.commands.access_data import AccessDataRequest
from src.core.models.application import Application, ApplicationCreate, ApplicationStatus, ApplicationUpdate
from src.core.models.application_custom_field import (
    ApplicationCustomField,
    ApplicationCustomFieldCreate,
    ApplicationCustomFieldUpdate,
)
from src.core.models.application_integration import ApplicationIntegration, ApplicationIntegrationCreate
from src.core.models.application_time_settings import (
    ApplicationTimeSettings,
    ApplicationTimeSettingsCreate,
    ApplicationTimeSettingsUpdate,
)
from src.core.models.draft import Draft, DraftCreate, DraftStatus, DraftUpdate
from src.core.models.drafted_player import DraftedPlayer, DraftedPlayerCreate
from src.core.models.event import Event, EventCreate, EventMatchType, EventStatus, EventUpdate, TeamFormation
from src.core.models.event_player import EventPlayer, EventPlayerCreate, EventPlayerStatus, EventPlayerUpdate
from src.core.models.filled_application_field import FilledApplicationField, FilledApplicationFieldCreate
from src.core.models.organizer import Organizer, OrganizerCreate
from src.core.models.player_role import PlayerRole, PlayerRoleCreate
from src.core.models.required_integration import RequiredIntegration, RequiredIntegrationCreate
from src.core.models.selected_game_role import SelectedGameRole, SelectedGameRoleCreate, SelectedGameRoleUpdate
from src.core.models.team import Team, TeamCreate
from src.core.models.team_player import TeamPlayer, TeamPlayerCreate


def make_access(
    *,
    server_id: UUID | None = None,
    member_id: UUID | None = None,
    permission_mask: int = 0,
    restriction_mask: int = 0,
    anonymous: bool = False,
) -> AccessDataRequest:
    return AccessDataRequest(
        member_id=None if anonymous else member_id or uuid4(),
        server_id=server_id or uuid4(),
        permission_mask=permission_mask,
        restriction_mask=restriction_mask,
    )


def make_organizer(event_id: UUID, *, member_id: UUID | None = None, id: UUID | None = None) -> Organizer:
    return Organizer(id=id or uuid4(), event_id=event_id, member_id=member_id or uuid4())


def make_event(
    *,
    id: UUID | None = None,
    server_id: UUID | None = None,
    name: str = "Test Event",
    match_type: EventMatchType = EventMatchType.SINGLE,
    use_application: bool = True,
    is_public: bool = True,
    team_size: int = 5,
    team_formation: TeamFormation = TeamFormation.BALANCE,
    status: EventStatus = EventStatus.CREATED,
    allow_multiple_drafts: bool = False,
    rating_set_id: UUID | None = None,
    organizer_member_ids: list[UUID] | None = None,
    organizers: list[Organizer] | None = None,
    required_integrations: list[RequiredIntegration] | None = None,
    selected_game_roles: list[SelectedGameRole] | None = None,
    custom_fields: list[ApplicationCustomField] | None = None,
    time_settings: ApplicationTimeSettings | None = None,
    applications: list[Application] | None = None,
    teams: list[Team] | None = None,
    drafts: list[Draft] | None = None,
    event_players: list[EventPlayer] | None = None,
) -> Event:
    event_id = id or uuid4()
    if organizers is None:
        organizers = [make_organizer(event_id, member_id=member_id) for member_id in (organizer_member_ids or [])]

    return Event(
        id=event_id,
        name=name,
        match_type=match_type,
        use_application=use_application,
        is_public=is_public,
        team_size=team_size,
        team_formation=team_formation,
        status=status,
        allow_multiple_drafts=allow_multiple_drafts,
        rating_set_id=rating_set_id,
        server_id=server_id or uuid4(),
        applications=applications or [],
        teams=teams or [],
        drafts=drafts or [],
        organizers=organizers,
        event_players=event_players or [],
        brackets=[],
        required_integrations=required_integrations or [],
        selected_game_roles=selected_game_roles or [],
        custom_fields=custom_fields or [],
        time_settings=time_settings,
    )


def make_application(
    event_id: UUID,
    *,
    id: UUID | None = None,
    member_id: UUID | None = None,
    status: ApplicationStatus = ApplicationStatus.PENDING,
    is_approved: bool | None = None,
    created_at: datetime | None = None,
    integrations: list[ApplicationIntegration] | None = None,
    filled_fields: list[FilledApplicationField] | None = None,
    event_player: EventPlayer | None = None,
) -> Application:
    return Application(
        id=id or uuid4(),
        event_id=event_id,
        member_id=member_id or uuid4(),
        is_approved=(status == ApplicationStatus.APPROVED) if is_approved is None else is_approved,
        status=status,
        created_at=created_at or datetime.now(timezone.utc),
        integrations=integrations or [],
        filled_fields=filled_fields or [],
        event_player=event_player,
    )


def make_custom_field(
    event_id: UUID,
    *,
    id: UUID | None = None,
    name: str = "Discord",
    is_private: bool = False,
    is_required: bool = False,
) -> ApplicationCustomField:
    return ApplicationCustomField(
        id=id or uuid4(),
        event_id=event_id,
        name=name,
        is_private=is_private,
        is_required=is_required,
    )


def make_required_integration(event_id: UUID, *, id: UUID | None = None, name: str = "discord") -> RequiredIntegration:
    return RequiredIntegration(id=id or uuid4(), name=name, event_id=event_id)


def make_selected_game_role(
    event_id: UUID,
    *,
    id: UUID | None = None,
    game_role_id: UUID | None = None,
    override_max_count: int | None = None,
    override_min_count: int | None = None,
) -> SelectedGameRole:
    return SelectedGameRole(
        id=id or uuid4(),
        game_role_id=game_role_id or uuid4(),
        event_id=event_id,
        override_max_count=override_max_count,
        override_min_count=override_min_count,
    )


def make_time_settings(
    event_id: UUID,
    *,
    id: UUID | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> ApplicationTimeSettings:
    return ApplicationTimeSettings(id=id or uuid4(), event_id=event_id, start_time=start_time, end_time=end_time)


def make_event_player(
    event_id: UUID,
    *,
    id: UUID | None = None,
    member_id: UUID | None = None,
    application_id: UUID | None = None,
    status: EventPlayerStatus = EventPlayerStatus.REGISTERED,
    is_draft_pinned: bool = False,
    player_roles: list[PlayerRole] | None = None,
) -> EventPlayer:
    return EventPlayer(
        id=id or uuid4(),
        event_id=event_id,
        member_id=member_id or uuid4(),
        application_id=application_id,
        is_draft_pinned=is_draft_pinned,
        status=status,
        player_roles=player_roles or [],
    )


def make_player_role(
    event_player_id: UUID,
    game_role_id: UUID,
    *,
    id: UUID | None = None,
    priority: int = 1,
    game_role: SelectedGameRole | None = None,
) -> PlayerRole:
    return PlayerRole(
        id=id or uuid4(),
        game_role_id=game_role_id,
        priority=priority,
        event_player_id=event_player_id,
        game_role=game_role,
    )


def make_filled_field(
    application_id: UUID,
    custom_field_id: UUID,
    *,
    id: UUID | None = None,
    value: str = "value",
) -> FilledApplicationField:
    return FilledApplicationField(
        id=id or uuid4(),
        value=value,
        custom_field_id=custom_field_id,
        application_id=application_id,
        created_at=datetime.now(timezone.utc),
    )


def make_application_integration(
    application_id: UUID,
    *,
    id: UUID | None = None,
    user_provider_id: UUID | None = None,
    provider_id: UUID | None = None,
    provider_name: str = "discord",
) -> ApplicationIntegration:
    return ApplicationIntegration(
        id=id or uuid4(),
        application_id=application_id,
        user_provider_id=user_provider_id or uuid4(),
        provider_id=provider_id or uuid4(),
        provider_name=provider_name,
    )


def make_draft(
    event_id: UUID,
    *,
    id: UUID | None = None,
    status: DraftStatus = DraftStatus.OPEN,
    drafted_players: list[DraftedPlayer] | None = None,
) -> Draft:
    return Draft(id=id or uuid4(), event_id=event_id, status=status, drafted_players=drafted_players or [])


def make_drafted_player(draft_id: UUID, event_player_id: UUID, *, id: UUID | None = None) -> DraftedPlayer:
    return DraftedPlayer(id=id or uuid4(), draft_id=draft_id, event_player_id=event_player_id)


def make_team(
    event_id: UUID,
    *,
    id: UUID | None = None,
    draft_id: UUID | None = None,
    name: str = "Team Alpha",
    players: list[TeamPlayer] | None = None,
) -> Team:
    return Team(id=id or uuid4(), event_id=event_id, draft_id=draft_id, name=name, players=players or [])


def make_team_player(
    team_id: UUID,
    *,
    id: UUID | None = None,
    member_id: UUID | None = None,
    game_role_id: UUID | None = None,
    rating: float = 1000.0,
) -> TeamPlayer:
    return TeamPlayer(
        id=id or uuid4(),
        team_id=team_id,
        member_id=member_id or uuid4(),
        game_role_id=game_role_id or uuid4(),
        rating=rating,
    )


class InMemoryEventRepository:
    def __init__(self, events: list[Event] | None = None):
        self.events = {event.id: event for event in (events or [])}

    async def create(self, data: EventCreate) -> Event:
        event = make_event(
            name=data.name,
            match_type=data.match_type,
            use_application=data.use_application,
            is_public=data.is_public,
            team_size=data.team_size,
            team_formation=data.team_formation,
            status=data.status,
            allow_multiple_drafts=data.allow_multiple_drafts,
            rating_set_id=data.rating_set_id,
            server_id=data.server_id,
        )
        self.events[event.id] = event
        return event

    async def get(self, field_id: UUID, **_kwargs) -> Event | None:
        return self.events.get(field_id)

    async def update(self, event_id: UUID, data: EventUpdate) -> Event:
        event = self.events[event_id]
        values = data.model_dump(exclude_unset=True)
        updated = event.model_copy(update=values)
        self.events[event_id] = updated
        return updated

    async def transition_status(self, event_id: UUID, status: EventStatus) -> Event:
        event = self.events[event_id].model_copy(update={"status": status})
        self.events[event_id] = event
        return event

    async def list_by_server(self, server_id: UUID, offset: int, limit: int) -> list[Event]:
        events = [event for event in self.events.values() if event.server_id == server_id]
        return events[offset:offset + limit]

    def replace(self, event: Event) -> None:
        self.events[event.id] = event

    def append_related(self, event_id: UUID, field_name: str, item) -> None:
        event = self.events.get(event_id)
        if event is None:
            return
        values = list(getattr(event, field_name) or [])
        values.append(item)
        self.replace(event.model_copy(update={field_name: values}))

    def replace_related(self, event_id: UUID, field_name: str, item) -> None:
        event = self.events.get(event_id)
        if event is None:
            return
        values = [existing for existing in (getattr(event, field_name) or []) if existing.id != item.id]
        values.append(item)
        self.replace(event.model_copy(update={field_name: values}))

    def remove_related(self, event_id: UUID, field_name: str, item_id: UUID) -> None:
        event = self.events.get(event_id)
        if event is None:
            return
        values = [existing for existing in (getattr(event, field_name) or []) if existing.id != item_id]
        self.replace(event.model_copy(update={field_name: values}))

    def set_time_settings(self, event_id: UUID, settings: ApplicationTimeSettings | None) -> None:
        event = self.events.get(event_id)
        if event is not None:
            self.replace(event.model_copy(update={"time_settings": settings}))


class InMemoryOrganizerRepository:
    def __init__(self, event_repo: InMemoryEventRepository):
        self._event_repo = event_repo
        self.organizers = {
            organizer.id: organizer
            for event in event_repo.events.values()
            for organizer in event.organizers
        }

    async def create(self, data: OrganizerCreate) -> Organizer:
        organizer = Organizer(id=uuid4(), event_id=data.event_id, member_id=data.member_id)
        self.organizers[organizer.id] = organizer
        self._event_repo.append_related(data.event_id, "organizers", organizer)
        return organizer

    async def list_by_event(self, event_id: UUID) -> list[Organizer]:
        event = self._event_repo.events.get(event_id)
        if event is not None:
            return list(event.organizers)
        return [organizer for organizer in self.organizers.values() if organizer.event_id == event_id]

    async def delete(self, organizer_id: UUID) -> bool:
        organizer = self.organizers.pop(organizer_id, None)
        if organizer is None:
            return False
        self._event_repo.remove_related(organizer.event_id, "organizers", organizer_id)
        return True


class InMemoryTimeSettingsRepository:
    def __init__(self, event_repo: InMemoryEventRepository):
        self._event_repo = event_repo
        self.settings = {
            event.time_settings.id: event.time_settings
            for event in event_repo.events.values()
            if event.time_settings is not None
        }

    async def create(self, data: ApplicationTimeSettingsCreate) -> ApplicationTimeSettings:
        settings = ApplicationTimeSettings(
            id=uuid4(),
            event_id=data.event_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        self.settings[settings.id] = settings
        self._event_repo.set_time_settings(data.event_id, settings)
        return settings

    async def get_by_event_id(self, event_id: UUID, **_kwargs) -> ApplicationTimeSettings | None:
        return next((settings for settings in self.settings.values() if settings.event_id == event_id), None)

    async def update(self, data: ApplicationTimeSettingsUpdate) -> ApplicationTimeSettings:
        settings = self.settings[data.id]
        updated = settings.model_copy(update=data.model_dump(exclude_unset=True, exclude={"id"}))
        self.settings[updated.id] = updated
        self._event_repo.set_time_settings(updated.event_id, updated)
        return updated


class InMemoryRequiredIntegrationRepository:
    def __init__(self, event_repo: InMemoryEventRepository):
        self._event_repo = event_repo
        self.integrations = {
            integration.id: integration
            for event in event_repo.events.values()
            for integration in event.required_integrations
        }

    async def create(self, data: RequiredIntegrationCreate) -> RequiredIntegration:
        integration = RequiredIntegration(id=uuid4(), name=data.name, event_id=data.event_id)
        self.integrations[integration.id] = integration
        self._event_repo.append_related(data.event_id, "required_integrations", integration)
        return integration

    async def get(self, integration_id: UUID, **_kwargs) -> RequiredIntegration | None:
        return self.integrations.get(integration_id)

    async def list_by_event(self, event_id: UUID) -> list[RequiredIntegration]:
        return [integration for integration in self.integrations.values() if integration.event_id == event_id]

    async def delete(self, integration_id: UUID) -> bool:
        integration = self.integrations.pop(integration_id, None)
        if integration is None:
            return False
        self._event_repo.remove_related(integration.event_id, "required_integrations", integration_id)
        return True


class InMemorySelectedGameRoleRepository:
    def __init__(self, event_repo: InMemoryEventRepository):
        self._event_repo = event_repo
        self.roles = {
            role.id: role
            for event in event_repo.events.values()
            for role in event.selected_game_roles
        }

    async def create(self, data: SelectedGameRoleCreate) -> SelectedGameRole:
        role = SelectedGameRole(
            id=uuid4(),
            game_role_id=data.game_role_id,
            event_id=data.event_id,
            override_max_count=data.override_max_count,
            override_min_count=data.override_min_count,
        )
        self.roles[role.id] = role
        self._event_repo.append_related(data.event_id, "selected_game_roles", role)
        return role

    async def get(self, role_id: UUID, **_kwargs) -> SelectedGameRole | None:
        return self.roles.get(role_id)

    async def list_by_event(self, event_id: UUID) -> list[SelectedGameRole]:
        return [role for role in self.roles.values() if role.event_id == event_id]

    async def update(self, data: SelectedGameRoleUpdate) -> SelectedGameRole:
        role = self.roles[data.id]
        updated = role.model_copy(update=data.model_dump(exclude_unset=True, exclude={"id"}))
        self.roles[updated.id] = updated
        self._event_repo.replace_related(updated.event_id, "selected_game_roles", updated)
        return updated

    async def delete(self, role_id: UUID) -> bool:
        role = self.roles.pop(role_id, None)
        if role is None:
            return False
        self._event_repo.remove_related(role.event_id, "selected_game_roles", role_id)
        return True


class InMemoryApplicationCustomFieldRepository:
    def __init__(self, event_repo: InMemoryEventRepository):
        self._event_repo = event_repo
        self.fields = {
            field.id: field
            for event in event_repo.events.values()
            for field in event.custom_fields
        }

    async def create(self, data: ApplicationCustomFieldCreate) -> ApplicationCustomField:
        field = ApplicationCustomField(
            id=uuid4(),
            event_id=data.event_id,
            name=data.name,
            is_private=data.is_private,
            is_required=data.is_required,
        )
        self.fields[field.id] = field
        self._event_repo.append_related(data.event_id, "custom_fields", field)
        return field

    async def get(self, field_id: UUID, **_kwargs) -> ApplicationCustomField | None:
        return self.fields.get(field_id)

    async def list_by_event(self, event_id: UUID) -> list[ApplicationCustomField]:
        return [field for field in self.fields.values() if field.event_id == event_id]

    async def update(self, data: ApplicationCustomFieldUpdate) -> ApplicationCustomField:
        field = self.fields[data.id]
        updated = field.model_copy(update=data.model_dump(exclude_unset=True, exclude={"id"}))
        self.fields[updated.id] = updated
        self._event_repo.replace_related(updated.event_id, "custom_fields", updated)
        return updated

    async def delete(self, field_id: UUID) -> bool:
        field = self.fields.pop(field_id, None)
        if field is None:
            return False
        self._event_repo.remove_related(field.event_id, "custom_fields", field_id)
        return True


class InMemoryApplicationRepository:
    def __init__(self, event_repo: InMemoryEventRepository | None = None, applications: list[Application] | None = None):
        self._event_repo = event_repo
        self.applications: dict[UUID, Application] = {}
        for application in applications or []:
            self.store(application)

    def store(self, application: Application) -> None:
        self.applications[application.id] = application
        if self._event_repo is not None and application.event_id in self._event_repo.events:
            self._event_repo.replace_related(application.event_id, "applications", application)

    async def create(self, data: ApplicationCreate) -> Application:
        application = make_application(
            data.event_id,
            member_id=data.member_id,
            status=data.status,
            is_approved=data.is_approved,
        )
        self.store(application)
        return application

    async def get(self, application_id: UUID, **_kwargs) -> Application | None:
        return self.applications.get(application_id)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> Application | None:
        return next(
            (
                application
                for application in self.applications.values()
                if application.event_id == event_id and application.member_id == member_id
            ),
            None,
        )

    async def update(self, data: ApplicationUpdate) -> Application:
        application = self.applications[data.id]
        updated = application.model_copy(update=data.model_dump(exclude_unset=True, exclude={"id"}))
        self.store(updated)
        return updated

    async def list_by_event(
        self,
        event_id: UUID,
        offset: int,
        limit: int,
        status: ApplicationStatus | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        **_kwargs,
    ) -> list[Application]:
        applications = [application for application in self.applications.values() if application.event_id == event_id]
        if status is not None:
            applications = [application for application in applications if application.status == status]
        if sort_by == "created_at":
            applications.sort(key=lambda application: application.created_at, reverse=sort_order == "desc")
        return applications[offset:offset + limit]


class InMemoryPlayerRepository:
    def __init__(
        self,
        event_repo: InMemoryEventRepository | None = None,
        application_repo: InMemoryApplicationRepository | None = None,
        players: list[EventPlayer] | None = None,
    ):
        self._event_repo = event_repo
        self._application_repo = application_repo
        self.players: dict[UUID, EventPlayer] = {}
        for player in players or []:
            self.store(player)

    def store(self, player: EventPlayer) -> None:
        self.players[player.id] = player
        if self._event_repo is not None and player.event_id in self._event_repo.events:
            self._event_repo.replace_related(player.event_id, "event_players", player)
        if self._application_repo is not None and player.application_id in self._application_repo.applications:
            application = self._application_repo.applications[player.application_id]
            self._application_repo.store(application.model_copy(update={"event_player": player}))

    async def create(self, data: EventPlayerCreate) -> EventPlayer:
        player = make_event_player(
            data.event_id,
            member_id=data.member_id,
            application_id=data.application_id,
            is_draft_pinned=data.is_draft_pinned,
        )
        self.store(player)
        return player

    async def get(self, player_id: UUID, **_kwargs) -> EventPlayer | None:
        return self.players.get(player_id)

    async def get_by_event_and_member(self, event_id: UUID, member_id: UUID) -> EventPlayer | None:
        return next(
            (player for player in self.players.values() if player.event_id == event_id and player.member_id == member_id),
            None,
        )

    async def list_by_event(
        self,
        event_id: UUID,
        offset: int,
        limit: int,
        status: EventPlayerStatus | None = None,
    ) -> list[EventPlayer]:
        players = [player for player in self.players.values() if player.event_id == event_id]
        if status is not None:
            players = [player for player in players if player.status == status]
        return players[offset:offset + limit]

    async def update(self, player_id: UUID, data: EventPlayerUpdate) -> EventPlayer:
        player = self.players[player_id]
        updated = player.model_copy(update=data.model_dump(exclude_unset=True))
        self.store(updated)
        return updated

    async def delete(self, player_id: UUID) -> bool:
        player = self.players.pop(player_id, None)
        if player is None:
            return False
        if self._event_repo is not None:
            self._event_repo.remove_related(player.event_id, "event_players", player_id)
        if self._application_repo is not None and player.application_id in self._application_repo.applications:
            application = self._application_repo.applications[player.application_id]
            self._application_repo.store(application.model_copy(update={"event_player": None}))
        return True


class InMemoryPlayerRoleRepository:
    def __init__(self, player_repo: InMemoryPlayerRepository):
        self._player_repo = player_repo
        self.roles: dict[UUID, PlayerRole] = {}

    async def create(self, data: PlayerRoleCreate) -> PlayerRole:
        role = PlayerRole(
            id=uuid4(),
            game_role_id=data.game_role_id,
            priority=data.priority,
            event_player_id=data.event_player_id,
        )
        self.roles[role.id] = role
        player = self._player_repo.players.get(data.event_player_id)
        if player is not None:
            roles = [existing for existing in player.player_roles if existing.id != role.id]
            roles.append(role)
            self._player_repo.store(player.model_copy(update={"player_roles": roles}))
        return role


class InMemoryFilledApplicationFieldRepository:
    def __init__(self, application_repo: InMemoryApplicationRepository):
        self._application_repo = application_repo
        self.fields: dict[UUID, FilledApplicationField] = {}

    async def create(self, data: FilledApplicationFieldCreate) -> FilledApplicationField:
        field = make_filled_field(data.application_id, data.custom_field_id, value=data.value)
        self.fields[field.id] = field
        application = self._application_repo.applications.get(data.application_id)
        if application is not None:
            fields = list(application.filled_fields)
            fields.append(field)
            self._application_repo.store(application.model_copy(update={"filled_fields": fields}))
        return field


class InMemoryApplicationIntegrationRepository:
    def __init__(self, application_repo: InMemoryApplicationRepository):
        self._application_repo = application_repo
        self.integrations: dict[UUID, ApplicationIntegration] = {}

    async def create(self, data: ApplicationIntegrationCreate) -> ApplicationIntegration:
        integration = ApplicationIntegration(
            id=uuid4(),
            application_id=data.application_id,
            user_provider_id=data.user_provider_id,
            provider_id=data.provider_id,
            provider_name=data.provider_name,
        )
        self.integrations[integration.id] = integration
        application = self._application_repo.applications.get(data.application_id)
        if application is not None:
            integrations = list(application.integrations)
            integrations.append(integration)
            self._application_repo.store(application.model_copy(update={"integrations": integrations}))
        return integration


class InMemoryDraftRepository:
    def __init__(self, drafts: list[Draft] | None = None):
        self.drafts = {draft.id: draft for draft in (drafts or [])}

    async def create(self, data: DraftCreate) -> Draft:
        draft = make_draft(data.event_id, status=data.status)
        self.drafts[draft.id] = draft
        return draft

    async def get(self, draft_id: UUID, **_kwargs) -> Draft | None:
        return self.drafts.get(draft_id)

    async def list_by_event(self, event_id: UUID, offset: int, limit: int) -> list[Draft]:
        drafts = [draft for draft in self.drafts.values() if draft.event_id == event_id]
        return drafts[offset:offset + limit]

    async def update(self, data: DraftUpdate) -> Draft:
        draft = self.drafts[data.id]
        updated = draft.model_copy(update=data.model_dump(exclude_unset=True, exclude={"id"}))
        self.drafts[updated.id] = updated
        return updated


class InMemoryDraftedPlayerRepository:
    def __init__(self, draft_repo: InMemoryDraftRepository):
        self._draft_repo = draft_repo
        self.drafted_players: dict[UUID, DraftedPlayer] = {}

    async def create(self, data: DraftedPlayerCreate) -> DraftedPlayer:
        drafted_player = DraftedPlayer(id=uuid4(), draft_id=data.draft_id, event_player_id=data.event_player_id)
        self.drafted_players[drafted_player.id] = drafted_player
        draft = self._draft_repo.drafts.get(data.draft_id)
        if draft is not None:
            drafted_players = list(draft.drafted_players)
            drafted_players.append(drafted_player)
            self._draft_repo.drafts[draft.id] = draft.model_copy(update={"drafted_players": drafted_players})
        return drafted_player


class InMemoryMatchRepository:
    def __init__(self, *, incomplete_count: int = 0, active_draft_ids: set[UUID] | None = None):
        self.incomplete_count = incomplete_count
        self.active_draft_ids = active_draft_ids or set()

    async def count_incomplete_matches_by_event(self, _event_id: UUID) -> int:
        return self.incomplete_count

    async def list_active_draft_ids_by_event(self, _event_id: UUID) -> set[UUID]:
        return set(self.active_draft_ids)


class InMemoryTeamRepository:
    def __init__(self, teams: list[Team] | None = None):
        self.teams = {team.id: team for team in (teams or [])}

    async def create(self, data: TeamCreate) -> Team:
        team = make_team(data.event_id, draft_id=data.draft_id, name=data.name)
        self.teams[team.id] = team
        return team

    async def get(self, team_id: UUID, **_kwargs) -> Team | None:
        return self.teams.get(team_id)

    async def list_by_event(self, event_id: UUID, offset: int, limit: int) -> list[Team]:
        teams = [team for team in self.teams.values() if team.event_id == event_id]
        return teams[offset:offset + limit]


class InMemoryTeamPlayerRepository:
    def __init__(self, team_repo: InMemoryTeamRepository):
        self._team_repo = team_repo
        self.team_players: dict[UUID, TeamPlayer] = {}

    async def create(self, data: TeamPlayerCreate) -> TeamPlayer:
        team_player = TeamPlayer(
            id=uuid4(),
            team_id=data.team_id,
            member_id=data.member_id,
            game_role_id=data.game_role_id,
            rating=data.rating,
        )
        self.team_players[team_player.id] = team_player
        team = self._team_repo.teams.get(data.team_id)
        if team is not None:
            players = list(team.players)
            players.append(team_player)
            self._team_repo.teams[team.id] = team.model_copy(update={"players": players})
        return team_player
