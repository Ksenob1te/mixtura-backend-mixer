"""
MatchService — individual match lifecycle: scheduling, scoring, resolution.

Every competitive interaction (a single game between two teams) is a Match.
Matches live inside a StageGroup and are wired together via MatchSlots.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from src.infra.postgre.models import (
    Match,
    MatchScore,
    MatchSlot,
    EventStatus,
)
from src.infra.postgre.repo import (
    EventRepository,
    MatchRepository,
    MatchScoreRepository,
    MatchSlotRepository,
    OrganizerRepository,
)
from ._base import BaseService

logger = logging.getLogger(__name__)

_MIN_SLOTS = 2  # A match always has at least 2 competitors


class MatchService(BaseService):
    """Handles the lifecycle of a single match — scheduling, scoring, winner resolution."""

    def __init__(
            self,
            match_repo: MatchRepository,
            match_slot_repo: MatchSlotRepository,
            match_score_repo: MatchScoreRepository,
            event_repo: EventRepository,
            organizer_repo: OrganizerRepository,
    ) -> None:
        self._match_repo = match_repo
        self._slot_repo = match_slot_repo
        self._score_repo = match_score_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo

    # ── private helpers ──────────────────────────

    async def _get_match_or_404(
            self,
            match_id: UUID,
            *,
            load_slots: bool = False,
            load_group: bool = False,
    ) -> Match:
        match = await self._match_repo.get(match_id, load_slots=load_slots, load_group=load_group)
        if match is None:
            raise NotFoundException("Match not found")
        return match

    async def _get_slot_by_num(self, match_id: UUID, slot_num: int) -> MatchSlot:
        slots = await self._slot_repo.list_by_match(match_id)
        slot = next((s for s in slots if s.slot_num == slot_num), None)
        if slot is None:
            raise NotFoundException(f"Slot {slot_num} not found in match {match_id}")
        return slot

    # ── read ─────────────────────────────────────

    async def get_match(self, match_id: UUID) -> Match:
        return await self._get_match_or_404(match_id, load_slots=True)

    async def list_matches_by_group(
            self,
            group_id: UUID,
            *,
            round_number: int | None = None,
    ) -> Sequence[Match]:
        matches = await self._match_repo.list_by_stage_group(group_id)
        if round_number is not None:
            return [m for m in matches if m.round_number == round_number]
        return matches

    async def get_match_slots(self, match_id: UUID) -> Sequence[MatchSlot]:
        await self._get_match_or_404(match_id)
        return await self._slot_repo.list_by_match(match_id)

    # ── scheduling ───────────────────────────────

    @BaseService.require_organizer
    async def schedule_match(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            scheduled_at: datetime,
    ) -> Match:
        match = await self._get_match_or_404(match_id)

        event = await self._event_repo.get(event_id)
        if event is None:
            raise NotFoundException("Event not found")

        if event.status not in [EventStatus.FORMATION, EventStatus.IN_PROGRESS]:
            raise BadRequestException(f"Cannot schedule match in {event.status} status")

        match.scheduled_at = scheduled_at
        match = await self._match_repo.update(match)
        logger.info("Match %s scheduled for %s", match_id, scheduled_at.isoformat())
        return match

    @BaseService.require_organizer
    async def reschedule_match(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            new_time: datetime,
    ) -> Match:
        match = await self._get_match_or_404(match_id)

        event = await self._event_repo.get(event_id)
        if event is None:
            raise NotFoundException("Event not found")
        
        if event.status not in [EventStatus.FORMATION, EventStatus.IN_PROGRESS]:
            raise BadRequestException(f"Cannot reschedule match in {event.status} status")

        if match.time_start is not None:
            raise ConflictException("Cannot reschedule a match that has already started")
        match.scheduled_at = new_time
        match = await self._match_repo.update(match)
        logger.info("Match %s rescheduled to %s", match_id, new_time.isoformat())
        return match

    # ── start / end ──────────────────────────────

    @BaseService.require_organizer
    async def start_match(self, event_id: UUID, issuer_id: UUID, match_id: UUID) -> Match:
        """Both slots must have teams assigned before the match can start."""
        match = await self._get_match_or_404(match_id)

        event = await self._event_repo.get(event_id)
        if event is None:
            raise NotFoundException("Event not found")
        
        # Auto-transition: FORMATION -> IN_PROGRESS
        if event.status == EventStatus.FORMATION:
            try:
                event.transition_to(EventStatus.IN_PROGRESS)
                event = await self._event_repo.update(event)
            except ValueError as e:
                raise BadRequestException(str(e))

        if event.status != EventStatus.IN_PROGRESS:
            raise BadRequestException(f"Cannot start match in {event.status} status (must be IN_PROGRESS)")

        if match.time_start is not None:
            raise ConflictException("Match has already started")

        slots = await self._slot_repo.list_by_match(match_id)
        if len(slots) < _MIN_SLOTS:
            raise BadRequestException(f"Match requires at least {_MIN_SLOTS} slots to start")

        for slot in slots:
            score = await self._score_repo.get_by_slot_id(slot.id)
            if score is None:
                raise BadRequestException(f"Slot {slot.slot_num} has no team assigned")

        match.time_start = datetime.now(timezone.utc)
        match = await self._match_repo.update(match)
        logger.info("Match %s started", match_id)
        return match

    @BaseService.require_organizer
    async def end_match(self, event_id: UUID, issuer_id: UUID, match_id: UUID) -> Match:
        match = await self._get_match_or_404(match_id)

        if match.time_start is None:
            raise ConflictException("Match has not started yet")
        if match.time_end is not None:
            raise ConflictException("Match has already ended")

        match.time_end = datetime.now(timezone.utc)
        match = await self._match_repo.update(match)

        # Check for event completion
        incomplete_count = await self._match_repo.count_incomplete_matches_by_event(event_id)
        if incomplete_count == 0:
            event = await self._event_repo.get(event_id)
            if event and event.status == EventStatus.IN_PROGRESS:
                try:
                    event.transition_to(EventStatus.COMPLETED)
                    await self._event_repo.update(event)
                    logger.info("Event %s completed (all matches finished)", event_id)
                except ValueError:
                    logger.warning("Could not auto-complete event %s", event_id)

        logger.info("Match %s ended", match_id)
        return match

    # ── score reporting ──────────────────────────

    @BaseService.require_organizer
    async def report_score(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            scores: dict[int, dict[str, UUID | int]],
    ) -> list[MatchScore]:
        """
        Report or update scores.

        *scores* maps ``slot_num`` → ``{"team_id": UUID, "score": int}``.
        """
        await self._get_match_or_404(match_id)
        
        event = await self._event_repo.get(event_id)
        if event is None:
            raise NotFoundException("Event not found")
        
        if event.status != EventStatus.IN_PROGRESS:
             raise BadRequestException(f"Cannot report scores in {event.status} status (must be IN_PROGRESS)")

        slots = await self._slot_repo.list_by_match(match_id)
        slot_map = {s.slot_num: s for s in slots}

        results: list[MatchScore] = []
        for slot_num, data in scores.items():
            slot = slot_map.get(slot_num)
            if slot is None:
                raise BadRequestException(f"Slot {slot_num} does not exist for this match")

            team_id: UUID = data["team_id"]  # type: ignore[assignment]
            score_val: int = data["score"]  # type: ignore[assignment]

            existing = await self._score_repo.get_by_slot_id(slot.id)
            if existing:
                existing.team_id = team_id
                existing.score = score_val
                results.append(await self._score_repo.update(existing))
            else:
                results.append(await self._score_repo.create(
                    MatchScore(slot_id=slot.id, team_id=team_id, score=score_val),
                ))

        logger.info("Match %s scores reported", match_id)
        return results

    @BaseService.require_organizer
    async def override_score(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            slot_num: int,
            score_val: int,
    ) -> MatchScore:
        match = await self._get_match_or_404(match_id)

        slot = await self._get_slot_by_num(match_id, slot_num)
        
        existing = await self._score_repo.get_by_slot_id(slot.id)
        if existing is None:
            raise BadRequestException("No score to override — report first")

        existing.score = score_val
        existing = await self._score_repo.update(existing)
        logger.info("Match %s slot %d score overridden to %d", match_id, slot_num, score_val)
        return existing

    # ── winner determination ─────────────────────

    async def determine_winner(self, match_id: UUID) -> UUID | None:
        """Return winner's ``team_id``, or ``None`` for draw / incomplete."""
        slots = await self._slot_repo.list_by_match(match_id)

        entries: list[MatchScore] = []
        for slot in slots:
            ms = await self._score_repo.get_by_slot_id(slot.id)
            if ms is None:
                return None
            entries.append(ms)

        if len(entries) < _MIN_SLOTS:
            return None

        entries.sort(key=lambda s: s.score, reverse=True)
        if entries[0].score == entries[1].score:
            return None  # Draw
        return entries[0].team_id

    # async def is_match_complete(self, match_id: UUID) -> bool:
    #     match = await self._get_match_or_404(match_id)
    #     if match.time_end is None:
    #         return False
    #     slots = await self._slot_repo.list_by_match(match_id)
    #     return all(
    #         await self._score_repo.get_by_slot_id(s.id) is not None
    #         for s in slots
    #     )

    # ── void / forfeit ───────────────────────────

    @BaseService.require_organizer
    async def void_match(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            reason: str = "",
    ) -> Match:
        """Nullify a match — remove scores and reset timestamps."""
        match = await self._get_match_or_404(match_id)

        for slot in await self._slot_repo.list_by_match(match_id):
            ms = await self._score_repo.get_by_slot_id(slot.id)
            if ms:
                await self._score_repo.delete(ms.id)

        match.time_start = None
        match.time_end = None
        match = await self._match_repo.update(match)
        logger.info("Match %s voided (reason=%s)", match_id, reason)
        return match

    @BaseService.require_organizer
    async def forfeit(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            forfeiting_team_id: UUID,
            default_score_winner: int = 1,
            default_score_loser: int = 0,
    ) -> list[MatchScore]:
        """Record a forfeit — the opposing team wins by default scores."""
        match = await self._get_match_or_404(match_id)

        slots = await self._slot_repo.list_by_match(match_id)
        if len(slots) < _MIN_SLOTS:
            raise BadRequestException(f"Match needs at least {_MIN_SLOTS} slots")

        scores: dict[int, dict[str, UUID | int]] = {}
        for slot in slots:
            existing = await self._score_repo.get_by_slot_id(slot.id)
            if existing is None:
                continue
            is_forfeiting = existing.team_id == forfeiting_team_id
            scores[slot.slot_num] = {
                "team_id": existing.team_id,
                "score": default_score_loser if is_forfeiting else default_score_winner,
            }

        if not scores:
            raise BadRequestException("Cannot forfeit — teams have not been assigned to match slots")

        result = await self.report_score(event_id, issuer_id, match_id, scores)

        # End the match immediately
        match = await self._get_match_or_404(match_id)
        if match.time_start is None:
            match.time_start = datetime.now(timezone.utc)
        match.time_end = datetime.now(timezone.utc)
        await self._match_repo.update(match)
        logger.info("Match %s: team %s forfeited", match_id, forfeiting_team_id)
        return result

    # ── slot assignment ──────────────────────────

    @BaseService.require_organizer
    async def assign_team_to_slot(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            slot_num: int,
            team_id: UUID,
    ) -> MatchScore:
        """Place a team into a match slot (creates a MatchScore stub with score=0)."""
        match = await self._get_match_or_404(match_id)

        slot = await self._get_slot_by_num(match_id, slot_num)

        existing = await self._score_repo.get_by_slot_id(slot.id)
        if existing:
            existing.team_id = team_id
            existing.score = 0
            return await self._score_repo.update(existing)

        ms = await self._score_repo.create(MatchScore(slot_id=slot.id, team_id=team_id, score=0))
        logger.info("Assigned team %s to match %s slot %d", team_id, match_id, slot_num)
        return ms

    @BaseService.require_organizer
    async def clear_slot(
            self,
            event_id: UUID,
            issuer_id: UUID,
            match_id: UUID,
            slot_num: int,
    ) -> None:
        match = await self._get_match_or_404(match_id)

        slot = await self._get_slot_by_num(match_id, slot_num)

        existing = await self._score_repo.get_by_slot_id(slot.id)
        if existing:
            await self._score_repo.delete(existing.id)
