import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ConflictException,
    InternalLogicException,
    NotFoundException,
)
from src.infra.postgre.exceptions import IntegrityForeignException, IntegrityUniqueException
from src.infra.postgre.models import (
    ApplicationCustomField,
    ApplicationTimeSettings,
    Event,
    EventStatus,
    Organizer,
    RequiredIntegration,
    SelectedGameRole,
    TeamFormation,
)
from src.infra.postgre.repo import (
    ApplicationCustomFieldRepository,
    ApplicationTimeSettingsRepository,
    EventRepository,
    OrganizerRepository,
    RequiredIntegrationRepository,
    SelectedGameRoleRepository,
)
from ._base import BaseService


class EventService(BaseService):
    """Creates, configures, publishes and cancels events."""

    def __init__(
            self,
            event_repo: EventRepository,
            organizer_repo: OrganizerRepository,
            time_settings_repo: ApplicationTimeSettingsRepository,
            integration_repo: RequiredIntegrationRepository,
            game_role_repo: SelectedGameRoleRepository,
            custom_field_repo: ApplicationCustomFieldRepository,
    ) -> None:
        self.logger = logging.getLogger(__name__)

        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._time_settings_repo = time_settings_repo
        self._integration_repo = integration_repo
        self._game_role_repo = game_role_repo
        self._custom_field_repo = custom_field_repo

    async def create_event(
            self,
            member_id: UUID,
            match_type: str,
            team_size: int,
            registration_type: str,
            team_formation: str | TeamFormation,
            is_public: bool = False,
            use_application: bool = False,
            allow_multiple_drafts: bool = False,
            rating_set_id: UUID | None = None,
    ) -> Event:
        """Create a new event and register member_id as the primary organizer."""
        if team_size < 1:
            raise BadRequestException("team_size must be at least 1")

        event = Event(
            match_type=match_type,
            use_application=use_application,
            is_public=is_public,
            team_size=team_size,
            registration_type=registration_type,
            team_formation=TeamFormation(team_formation),
            allow_multiple_drafts=allow_multiple_drafts,
            rating_set_id=rating_set_id,
        )
        try:
            event = await self._event_repo.create(event)
        except IntegrityForeignException:
            raise BadRequestException("Invalid rating_set reference")

        await self._organizer_repo.create(
            Organizer(event_id=event.id, member_id=member_id),
        )
        self.logger.info("Event %s created by %s (type=%s)", event.id, member_id, match_type)
        return event

    async def get_event(self, event_id: UUID) -> Event:
        """Return event with organizers & basic configuration loaded."""
        return await self._fetch_event(
            event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
        )

    async def get_event_full(self, event_id: UUID) -> Event:
        """Return event with all  relationships loaded (organizer dashboard)."""
        return await self._fetch_event(
            event_id,
            load_organizers=True,
            load_integrations=True,
            load_time_settings=True,
            load_game_roles=True,
            load_custom_fields=True,
            load_applications=True,
            load_teams=True,
            load_drafts=True,
            load_players=True,
            load_brackets=True,
        )

    async def list_public_events(self, offset: int = 0, limit: int = 50) -> Sequence[Event]:
        return await self._event_repo.list_public(offset, limit)

    @BaseService.require_organizer
    async def update_config(
            self,
            event_id: UUID,
            issuer_id: UUID,
            is_public: bool | None = None,
    ) -> Event:
        """Partial-update basic event configuration. Organizer only."""
        event = await self._fetch_event(event_id)

        if is_public is not None:
            event.is_public = is_public

        event = await self._event_repo.update(event)
        self.logger.info("Event %s config updated by %s", event_id, issuer_id)
        return event

    @BaseService.require_organizer
    async def add_organizer(
            self,
            event_id: UUID,
            issuer_id: UUID,
            target_member_id: UUID
    ) -> Organizer:
        """Add a co-organizer. Requester must already be an organizer."""
        _ = issuer_id  # used by @require_organizer
        await self._fetch_event(event_id)

        try:
            return await self._organizer_repo.create(
                Organizer(event_id=event_id, member_id=target_member_id),
            )
        except IntegrityUniqueException:
            raise ConflictException("Member is already an organizer")

    @BaseService.require_organizer
    async def remove_organizer(self, event_id: UUID, issuer_id: UUID, target_member_id: UUID) -> None:
        """Remove a co-organizer. Cannot remove the last remaining one."""
        _ = issuer_id  # used by @require_organizer
        await self._fetch_event(event_id)

        organizers = await self._organizer_repo.list_by_event(event_id)
        if len(organizers) <= 1:
            raise BadRequestException("Cannot remove the last organizer")

        result = await self._organizer_repo.delete(target_member_id)

        if not result:
            raise NotFoundException("Organizer not found")

    async def list_organizers(self, event_id: UUID) -> Sequence[Organizer]:
        await self._fetch_event(event_id)
        return await self._organizer_repo.list_by_event(event_id)

    @BaseService.require_organizer
    async def set_time_settings(
            self,
            event_id: UUID,
            issuer_id: UUID,
            start_time: datetime | None = None,
            end_time: datetime | None = None,
    ) -> ApplicationTimeSettings:
        """Set or replace the registration / check-in time window."""
        _ = issuer_id  # used by @require_organizer
        await self._fetch_event(event_id)

        if start_time and end_time and end_time <= start_time:
            raise BadRequestException("end_time must be after start_time")

        existing = await self._time_settings_repo.get_by_event_id(event_id)
        if existing:
            existing.start_time = start_time
            existing.end_time = end_time
            return await self._time_settings_repo.update(existing)

        return await self._time_settings_repo.create(
            ApplicationTimeSettings(event_id=event_id, start_time=start_time, end_time=end_time),
        )

    # ── required integrations ────────────────────

    @BaseService.require_organizer
    async def set_required_integrations(
            self,
            event_id: UUID,
            issuer_id: UUID,
            integration_names: list[str],
    ) -> list[RequiredIntegration]:
        """Replace the full set of required integrations (idempotent sync)."""
        await self._fetch_event(event_id)

        existing = await self._integration_repo.list_by_event(event_id)
        existing_by_name = {i.name: i for i in existing}
        desired = set(integration_names)

        for item in existing:
            if item.name not in desired:
                await self._integration_repo.delete(item.id)

        for name in desired - existing_by_name.keys():
            await self._integration_repo.create(
                RequiredIntegration(name=name, event_id=event_id),
            )

        return list(await self._integration_repo.list_by_event(event_id))

    # ── game roles ───────────────────────────────

    @BaseService.require_organizer
    async def set_selected_game_roles(
            self,
            event_id: UUID,
            issuer_id: UUID,
            roles: list[dict],
    ) -> list[SelectedGameRole]:
        """
        Sync selected game roles.

        Each dict: ``{"game_role_id": UUID, "override_min_count": int|None, "override_max_count": int|None}``
        """
        await self._fetch_event(event_id)

        existing = await self._game_role_repo.list_by_event(event_id)
        existing_map = {r.game_role_id: r for r in existing}
        incoming_ids = {r["game_role_id"] for r in roles}

        for role in existing:
            if role.game_role_id not in incoming_ids:
                await self._game_role_repo.delete(role.id)

        result: list[SelectedGameRole] = []
        for r in roles:
            gid = r["game_role_id"]
            if gid in existing_map:
                obj = existing_map[gid]
                obj.override_min_count = r.get("override_min_count")
                obj.override_max_count = r.get("override_max_count")
                result.append(await self._game_role_repo.update(obj))
            else:
                result.append(await self._game_role_repo.create(SelectedGameRole(
                    game_role_id=gid,
                    event_id=event_id,
                    override_min_count=r.get("override_min_count"),
                    override_max_count=r.get("override_max_count"),
                )))
        return result

    # ── custom application fields ────────────────

    @BaseService.require_organizer
    async def set_custom_fields(
            self,
            event_id: UUID,
            issuer_id: UUID,
            fields: list[dict],
    ) -> list[ApplicationCustomField]:
        """
        Sync custom form fields (delete + recreate).

        Each dict: ``{"name": str, "is_required": bool, "is_private": bool}``
        """
        await self._fetch_event(event_id)

        for cf in await self._custom_field_repo.list_by_event(event_id):
            await self._custom_field_repo.delete(cf.id)

        return [
            await self._custom_field_repo.create(ApplicationCustomField(
                event_id=event_id,
                name=f["name"],
                is_required=f.get("is_required", False),
                is_private=f.get("is_private", False),
            ))
            for f in fields
        ]

    # ── lifecycle transitions ────────────────────

    @BaseService.require_organizer
    async def publish_event(self, event_id: UUID, issuer_id: UUID) -> Event:
        """DRAFT → REGISTRATION_OPEN. Validates minimal configuration."""
        event = await self._fetch_event(event_id)

        if event.team_size < 1:
            raise BadRequestException("team_size must be configured before publishing")

        if event.match_type == "TOURNAMENT":
            ts = await self._time_settings_repo.get_by_event_id(event_id)
            if ts is None or ts.start_time is None:
                raise BadRequestException("Tournament events require a registration time window")

        try:
            event.open_registration()
        except ValueError as e:
            raise BadRequestException(str(e))

        event = await self._event_repo.update(event)
        self.logger.info("Event %s published by %s", event_id, issuer_id)
        return event

    @BaseService.require_organizer
    async def cancel_event(self, event_id: UUID, issuer_id: UUID, reason: str = "") -> Event:
        """Cancel the event."""
        event = await self._fetch_event(event_id)

        try:
            event.cancel_event()
        except ValueError as e:
            raise BadRequestException(str(e))

        event = await self._event_repo.update(event)
        self.logger.info("Event %s cancelled by %s (reason=%s)", event_id, issuer_id, reason)
        return event

    # ── clone ────────────────────────────────────

    async def clone_event(self, source_event_id: UUID, issuer_id: UUID) -> Event:
        """Deep-copy settings into a fresh event (players/teams/drafts are NOT copied)."""
        source = await self._fetch_event(
            source_event_id,
            load_integrations=True,
            load_game_roles=True,
            load_custom_fields=True,
        )
        await self._assert_organizer(source_event_id, issuer_id)

        new_event = await self.create_event(
            member_id=issuer_id,
            match_type=source.match_type,
            team_size=source.team_size,
            registration_type=source.registration_type,
            team_formation=source.team_formation.value,
            is_public=source.is_public,
            use_application=source.use_application,
            allow_multiple_drafts=source.allow_multiple_drafts,
            rating_set_id=source.rating_set_id,
        )

        for integ in source.required_integrations:
            await self._integration_repo.create(
                RequiredIntegration(name=integ.name, event_id=new_event.id),
            )
        for role in source.selected_game_roles:
            await self._game_role_repo.create(SelectedGameRole(
                game_role_id=role.game_role_id,
                event_id=new_event.id,
                override_min_count=role.override_min_count,
                override_max_count=role.override_max_count,
            ))
        for cf in source.custom_fields:
            await self._custom_field_repo.create(ApplicationCustomField(
                event_id=new_event.id,
                name=cf.name,
                is_required=cf.is_required,
                is_private=cf.is_private,
            ))

        self.logger.info("Event %s cloned from %s by %s", new_event.id, source_event_id, issuer_id)
        return new_event

    @BaseService.require_organizer
    async def delete_event(self, event_id: UUID, issuer_id: UUID) -> None:
        """Hard-delete event and all cascading children."""
        await self._fetch_event(event_id)
        if not await self._event_repo.delete(event_id):
            raise InternalLogicException("Failed to delete event")
        self.logger.info("Event %s deleted by %s", event_id, issuer_id)
