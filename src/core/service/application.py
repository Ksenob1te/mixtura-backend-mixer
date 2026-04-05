import logging
from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from src.infra.postgre.exceptions import IntegrityUniqueException
from src.infra.postgre.models import (
    Application,
    ApplicationIntegration,
    Event,
    EventPlayer,
    FilledApplicationField,
)
from src.infra.postgre.models.application import ApplicationStatus
from src.infra.postgre.models.event import EventStatus
from src.infra.postgre.repo import (
    ApplicationCustomFieldRepository,
    ApplicationIntegrationRepository,
    ApplicationRepository,
    ApplicationTimeSettingsRepository,
    EventRepository,
    FilledApplicationFieldRepository,
    OrganizerRepository,
    PlayerRepository,
)
from ._base import BaseService

logger = logging.getLogger(__name__)


class ApplicationService(BaseService):
    def __init__(
            self,
            application_repo: ApplicationRepository,
            event_repo: EventRepository,
            organizer_repo: OrganizerRepository,
            player_repo: PlayerRepository,
            filled_field_repo: FilledApplicationFieldRepository,
            custom_field_repo: ApplicationCustomFieldRepository,
            integration_repo: ApplicationIntegrationRepository,
            time_settings_repo: ApplicationTimeSettingsRepository,
    ) -> None:
        self._app_repo = application_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._player_repo = player_repo
        self._filled_field_repo = filled_field_repo
        self._custom_field_repo = custom_field_repo
        self._integration_repo = integration_repo
        self._time_settings_repo = time_settings_repo

    # ── private helpers ──────────────────────────

    async def _assert_registration_open(self, event: Event) -> None:
        if event.status != EventStatus.REGISTRATION:
            raise BadRequestException(f"Event registration is not open (status: {event.status})")

        ts = await self._time_settings_repo.get_by_event_id(event.id)
        if ts is None:
            return  # No window → always open
        now = datetime.now(timezone.utc)
        if ts.start_time and now < ts.start_time.replace(tzinfo=timezone.utc):
            raise BadRequestException("Registration has not started yet")
        if ts.end_time and now > ts.end_time.replace(tzinfo=timezone.utc):
            raise BadRequestException("Registration has ended")

    # async def _assert_no_duplicate(self, event_id: UUID, member_id: UUID) -> None:
    #     existing = await self._app_repo.get_by_event_and_member(event_id, member_id)
    #     if existing is not None:
    #         raise ConflictException("You have already applied to this event")

    async def _ensure_event_player(self, application: Application) -> EventPlayer:
        existing = await self._player_repo.get_by_event_and_member(
            application.event_id, application.member_id,
        )
        if existing is not None:
            return existing

        return await self._player_repo.create(EventPlayer(
            event_id=application.event_id,
            member_id=application.member_id,
            application_id=application.id,
        ))

    async def _remove_event_player(self, event_id: UUID, member_id: UUID) -> None:
        player = await self._player_repo.get_by_event_and_member(event_id, member_id)
        if player is not None:
            await self._player_repo.delete(player.id)

    # ── quick join (MIX) ─────────────────────────

    async def quick_join(self, event_id: UUID, member_id: UUID) -> Application:
        """
        Instant join for MIX events.

        Creates an APPROVED Application and an EventPlayer in one step.
        """
        event = await self._fetch_event(event_id)
        await self._assert_no_duplicate(event_id, member_id)
        await self._assert_registration_open(event)

        # Capacity check
        player_count = await self._player_repo.count(EventPlayer.event_id == event_id)
        max_players = event.team_size * 10
        if player_count >= max_players:
            raise ConflictException("Event lobby is full")

        application = Application(
            event_id=event_id,
            member_id=member_id,
            status=ApplicationStatus.APPROVED,
            is_approved=True,
        )
        try:
            application = await self._app_repo.create(application)
        except IntegrityUniqueException:
            raise ConflictException("You have already applied to this event")

        await self._player_repo.create(EventPlayer(
            event_id=event_id,
            member_id=member_id,
            application_id=application.id,
        ))
        logger.info("Member %s quick-joined event %s", member_id, event_id)
        return application

    # ── formal application (TOURNAMENT) ──────────

    async def submit_application(
            self,
            event_id: UUID,
            member_id: UUID,
            *,
            filled_fields: list[dict] | None = None,
            integration_ids: list[UUID] | None = None,
    ) -> Application:
        """
        Submit a formal tournament application.

        *filled_fields*: ``[{"custom_field_id": UUID, "value": str}, ...]``
        *integration_ids*: external user-provider IDs to attach.
        """
        event = await self._fetch_event(event_id)
        await self._assert_no_duplicate(event_id, member_id)
        await self._assert_registration_open(event)

        # Validate required custom fields
        if event.use_application:
            all_fields = await self._custom_field_repo.list_by_event(event_id)
            required_ids = {f.id for f in all_fields if f.is_required}
            provided_ids = {f["custom_field_id"] for f in (filled_fields or [])}
            missing = required_ids - provided_ids
            if missing:
                raise BadRequestException(f"Missing required fields: {missing}")

        application = Application(
            event_id=event_id,
            member_id=member_id,
            status=ApplicationStatus.PENDING,
            is_approved=False,
        )
        try:
            application = await self._app_repo.create(application)
        except IntegrityUniqueException:
            raise ConflictException("You have already applied to this event")

        for ff in filled_fields or []:
            await self._filled_field_repo.create(FilledApplicationField(
                application_id=application.id,
                custom_field_id=ff["custom_field_id"],
                value=str(ff["value"]),
            ))
        for uid in integration_ids or []:
            await self._integration_repo.create(ApplicationIntegration(
                application_id=application.id,
                user_provider_id=uid,
            ))

        logger.info("Member %s submitted application for event %s", member_id, event_id)
        return application

    # ── status management (organizer) ────────────

    @BaseService.require_organizer
    async def manage_status(
            self,
            event_id: UUID,
            issuer_id: UUID,
            application_id: UUID,
            new_status: ApplicationStatus,
    ) -> Application:
        """Approve / reject / waitlist a single application."""
        application = await self._app_repo.get(application_id)
        if application is None:
            raise NotFoundException("Application not found")
        if application.event_id != event_id:
            raise BadRequestException("Application does not belong to the specified event")

        application.status = new_status
        application.is_approved = new_status == ApplicationStatus.APPROVED
        application = await self._app_repo.update(application)

        if new_status == ApplicationStatus.APPROVED:
            await self._ensure_event_player(application)

        logger.info(
            "Application %s → %s (by %s)", application_id, new_status.value, issuer_id,
        )
        return application

    async def bulk_approve(
            self,
            event_id: UUID,
            organizer_id: UUID,
            *,
            status_filter: ApplicationStatus = ApplicationStatus.PENDING,
            limit: int | None = None,
    ) -> list[Application]:
        """Approve applications matching *status_filter*, up to *limit*."""
        await self._fetch_event(event_id)
        await self._assert_organizer(event_id, organizer_id)

        all_apps = await self._app_repo.list_by_event(event_id)
        targets = [a for a in all_apps if a.status == status_filter]
        if limit is not None:
            targets = targets[:limit]

        approved: list[Application] = []
        for app in targets:
            app.status = ApplicationStatus.APPROVED
            app.is_approved = True
            app = await self._app_repo.update(app)
            await self._ensure_event_player(app)
            approved.append(app)

        logger.info("Bulk approved %d applications for event %s", len(approved), event_id)
        return approved

    async def bulk_reject(
            self,
            event_id: UUID,
            organizer_id: UUID,
            *,
            status_filter: ApplicationStatus = ApplicationStatus.PENDING,
    ) -> int:
        """Reject all applications with the given status. Returns count."""
        await self._fetch_event(event_id)
        await self._assert_organizer(event_id, organizer_id)

        all_apps = await self._app_repo.list_by_event(event_id)
        targets = [a for a in all_apps if a.status == status_filter]

        for app in targets:
            app.status = ApplicationStatus.REJECTED
            app.is_approved = False
            await self._app_repo.update(app)

        logger.info("Bulk rejected %d applications for event %s", len(targets), event_id)
        return len(targets)

    async def check_in(self, event_id: UUID, member_id: UUID) -> Application:
        """Mark an approved player as present before the event starts."""
        await self._fetch_event(event_id)

        app = await self._app_repo.get_by_event_and_member(event_id, member_id)
        if app is None:
            raise NotFoundException("Application not found for this member")
        if app.status != ApplicationStatus.APPROVED:
            raise BadRequestException("Only approved applications can check in")

        ts = await self._time_settings_repo.get_by_event_id(event_id)
        if ts and ts.end_time:
            now = datetime.now(timezone.utc)
            if now > ts.end_time.replace(tzinfo=timezone.utc):
                raise BadRequestException("Check-in window has closed")

        await self._ensure_event_player(app)
        logger.info("Member %s checked in for event %s", member_id, event_id)
        return app

    # ── kick / leave ─────────────────────────────

    async def kick_applicant(
            self,
            event_id: UUID,
            organizer_id: UUID,
            target_member_id: UUID,
            reason: str = "",
    ) -> None:
        """Organizer kicks a player — rejects application and removes EventPlayer."""
        await self._fetch_event(event_id)
        await self._assert_organizer(event_id, organizer_id)

        app = await self._app_repo.get_by_event_and_member(event_id, target_member_id)
        if app is None:
            raise NotFoundException("Target member has no application")

        app.status = ApplicationStatus.REJECTED
        app.is_approved = False
        await self._app_repo.update(app)
        await self._remove_event_player(event_id, target_member_id)

        logger.info(
            "Organizer %s kicked %s from event %s (reason=%s)",
            organizer_id, target_member_id, event_id, reason,
        )

    async def leave_event(self, event_id: UUID, member_id: UUID) -> None:
        """Player voluntarily leaves the event."""
        app = await self._app_repo.get_by_event_and_member(event_id, member_id)
        if app is None:
            raise NotFoundException("You have no application for this event")

        await self._remove_event_player(event_id, member_id)
        await self._app_repo.delete(app.id)
        logger.info("Member %s left event %s", member_id, event_id)

    async def get_waitlist(self, event_id: UUID) -> list[Application]:
        """Return waitlisted applications in FIFO order."""
        all_apps = await self._app_repo.list_by_event(event_id)
        return [a for a in all_apps if a.status == ApplicationStatus.WAITLIST]

    async def promote_from_waitlist(
            self,
            event_id: UUID,
            organizer_id: UUID,
            count: int = 1,
    ) -> list[Application]:
        """Promote the top *count* waitlisted players to APPROVED."""
        await self._fetch_event(event_id)
        await self._assert_organizer(event_id, organizer_id)

        waitlist = await self.get_waitlist(event_id)
        promoted: list[Application] = []
        for app in waitlist[:count]:
            app.status = ApplicationStatus.APPROVED
            app.is_approved = True
            app = await self._app_repo.update(app)
            await self._ensure_event_player(app)
            promoted.append(app)
        return promoted

    # ── listing / stats ──────────────────────────

    async def list_applications(
            self,
            event_id: UUID,
            *,
            status_filter: ApplicationStatus | None = None,
            offset: int = 0,
            limit: int = 100,
    ) -> Sequence[Application]:
        """Paginated listing, optionally filtered by status."""
        if status_filter is not None:
            return await self._app_repo.list(
                offset, limit, None,
                Application.event_id == event_id,
                Application.status == status_filter,
            )
        return await self._app_repo.list_by_event(event_id, offset=offset, limit=limit)

    async def count_by_status(self, event_id: UUID) -> dict[str, int]:
        """Return ``{status_name: count}`` for the organizer dashboard."""
        return {
            s.value: await self._app_repo.count_by_event_and_status(event_id, s)
            for s in ApplicationStatus
        }

    async def get_application_detail(self, application_id: UUID) -> Application:
        """Return a single application with filled fields & integrations."""
        app = await self._app_repo.get(
            application_id,
            load_filled_fields=True,
            load_integrations=True,
            load_event_player=True,
        )
        if app is None:
            raise NotFoundException("Application not found")
        return app
