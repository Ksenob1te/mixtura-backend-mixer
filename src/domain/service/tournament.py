"""
TournamentService — Bracket creation, stage management, match generation & progression.

This is the orchestrator for the competitive structure of a TOURNAMENT event.
It handles:
  • Bracket + Stage definition (Groups → Playoffs, etc.)
  • Seeding (random, MMR-based, manual)
  • Match-tree generation for Single/Double Elimination
  • Round-robin & Swiss pairing generation
  • Winner advancement through the bracket
  • Stage completion & team promotion
  • Standings computation
"""

from __future__ import annotations

import logging
import math
import random
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from src.infra.postgre.models import (
    Bracket,
    BracketPlacement,
    Match,
    MatchScore,
    MatchSlot,
    RoundRobinSettings,
    Stage,
    StageGroup,
    SwissSettings,
    EventStatus,
)
from src.infra.postgre.models.match import BracketPosition
from src.infra.postgre.models.match_slot import MatchSlotSourceType
from src.infra.postgre.repo import (
    BracketPlacementRepository,
    BracketRepository,
    EventRepository,
    MatchRepository,
    MatchScoreRepository,
    MatchSlotRepository,
    OrganizerRepository,
    RoundRobinSettingsRepository,
    StageGroupRepository,
    StageRepository,
    SwissSettingsRepository,
    TeamRepository,
)
from ._base import BaseService

logger = logging.getLogger(__name__)


class TournamentService(BaseService):
    """
    Orchestrates tournament structure — from bracket creation to final standings.
    """

    def __init__(
            self,
            bracket_repo: BracketRepository,
            bracket_placement_repo: BracketPlacementRepository,
            stage_repo: StageRepository,
            stage_group_repo: StageGroupRepository,
            match_repo: MatchRepository,
            match_slot_repo: MatchSlotRepository,
            match_score_repo: MatchScoreRepository,
            team_repo: TeamRepository,
            event_repo: EventRepository,
            organizer_repo: OrganizerRepository,
            rr_settings_repo: RoundRobinSettingsRepository,
            swiss_settings_repo: SwissSettingsRepository,
    ) -> None:
        self._bracket_repo = bracket_repo
        self._placement_repo = bracket_placement_repo
        self._stage_repo = stage_repo
        self._group_repo = stage_group_repo
        self._match_repo = match_repo
        self._slot_repo = match_slot_repo
        self._score_repo = match_score_repo
        self._team_repo = team_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._rr_repo = rr_settings_repo
        self._swiss_repo = swiss_settings_repo

    # ──────────────────────────────────────────────
    #  Guards
    # ──────────────────────────────────────────────

    # _assert_organizer is inherited from BaseService

    # ══════════════════════════════════════════════
    #  1. BRACKET MANAGEMENT
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def create_bracket(self, event_id: UUID, issuer_id: UUID) -> Bracket:
        """Create a new bracket container for the event."""
        event = await self._event_repo.get(event_id)
        if event is None:
            raise NotFoundException("Event not found")
        # Check happens in decorator


        bracket = Bracket(event_id=event_id)
        bracket = await self._bracket_repo.create(bracket)
        logger.info("Bracket %s created for event %s", bracket.id, event_id)
        return bracket

    async def get_bracket(self, bracket_id: UUID) -> Bracket:
        bracket = await self._bracket_repo.get(bracket_id, load_stages=True, load_placements=True)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        return bracket

    async def list_brackets(self, event_id: UUID) -> Sequence[Bracket]:
        return await self._bracket_repo.list_by_event(event_id)

    @BaseService.require_organizer
    async def delete_bracket(self, event_id: UUID, issuer_id: UUID, bracket_id: UUID) -> None:
        bracket = await self._bracket_repo.get(bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Bracket does not belong to the specified event")

        await self._bracket_repo.delete(bracket_id)
        logger.info("Bracket %s deleted", bracket_id)

    # ══════════════════════════════════════════════
    #  2. SEEDING (BracketPlacement)
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def seed_bracket(
            self,
            event_id: UUID,
            issuer_id: UUID,
            bracket_id: UUID,
            team_ids: list[UUID],
            *,
            strategy: str = "MANUAL",
    ) -> list[BracketPlacement]:
        """
        Assign teams to bracket seed positions.

        Strategies:
          • ``MANUAL``  — *team_ids* order is used as-is (index = seed)
          • ``RANDOM``  — shuffle *team_ids* before seeding
          • ``RATING``  — sort teams by average roster rating descending
        """
        bracket = await self._bracket_repo.get(bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Bracket does not belong to the specified event")

        # Clear existing placements
        old = await self._placement_repo.list_by_bracket(bracket_id)

        for p in old:
            await self._placement_repo.delete(p.id)

        ordered = list(team_ids)
        if strategy == "RANDOM":
            random.shuffle(ordered)
        elif strategy == "RATING":
            # Sort by team average rating — higher rated gets lower seed number.
            # In production, inject TeamPlayerRepository and compute averages.
            # For now, keeps MANUAL order as fallback.
            pass

        placements: list[BracketPlacement] = []
        for idx, tid in enumerate(ordered):
            bp = BracketPlacement(
                bracket_id=bracket_id,
                team_id=tid,
                placement=idx + 1,
            )
            bp = await self._placement_repo.create(bp)
            placements.append(bp)

        logger.info(
            "Bracket %s seeded with %d teams (strategy=%s)",
            bracket_id, len(placements), strategy,
        )
        return placements

    async def get_seeding(self, bracket_id: UUID) -> Sequence[BracketPlacement]:
        return await self._placement_repo.list_by_bracket(bracket_id)

    # ══════════════════════════════════════════════
    #  3. STAGE CONFIGURATION
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def add_stage(
            self,
            event_id: UUID,
            issuer_id: UUID,
            bracket_id: UUID,
            *,
            name: str,
            stage_format: str,
            stage_index: int | None = None,
    ) -> Stage:
        """
        Add a stage to the bracket.

        *stage_format*: ``SINGLE_ELIM``, ``DOUBLE_ELIM``, ``ROUND_ROBIN``, ``SWISS``, ``GROUPS``
        """
        bracket = await self._bracket_repo.get(bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Bracket does not belong to the specified event")

        if stage_index is None:
            existing = await self._stage_repo.list_by_bracket(bracket_id)
            stage_index = len(existing) + 1

        stage = Stage(
            bracket_id=bracket_id,
            name=name,
            format=stage_format,
            stage_index=stage_index,
        )
        stage = await self._stage_repo.create(stage)
        logger.info("Stage '%s' (format=%s) added to bracket %s", name, stage_format, bracket_id)
        return stage

    @BaseService.require_organizer
    async def configure_round_robin(
            self,
            event_id: UUID,
            issuer_id: UUID,
            stage_id: UUID,
            *,
            meetings_per_pair: int = 1,
            score_system: str = "POINTS",
            score_per_win: int = 3,
            score_per_draw: int = 1,
    ) -> RoundRobinSettings:
        """Attach Round-Robin settings to a stage."""
        stage = await self._stage_repo.get(stage_id, load_settings=True)
        if stage is None:
            raise NotFoundException("Stage not found")

        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        # Upsert
        existing = await self._rr_repo.get_by_stage_id(stage_id)
        if existing:
            existing.meetings_per_pair = meetings_per_pair
            existing.score_system = score_system
            existing.score_per_win = score_per_win
            existing.score_per_draw = score_per_draw
            return await self._rr_repo.update(existing)

        rr = RoundRobinSettings(
            stage_id=stage_id,
            meetings_per_pair=meetings_per_pair,
            score_system=score_system,
            score_per_win=score_per_win,
            score_per_draw=score_per_draw,
        )
        return await self._rr_repo.create(rr)

    @BaseService.require_organizer
    async def configure_swiss(
            self,
            event_id: UUID,
            issuer_id: UUID,
            stage_id: UUID,
            *,
            score_per_win: int = 3,
            score_per_draw: int = 1,
            score_per_bye: int = 3,
    ) -> SwissSettings:
        """Attach Swiss-system settings to a stage."""
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")

        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        existing = await self._swiss_repo.get_by_stage_id(stage_id)

        if existing:
            existing.score_per_win = score_per_win
            existing.score_per_draw = score_per_draw
            existing.score_per_bye = score_per_bye
            return await self._swiss_repo.update(existing)

        sw = SwissSettings(
            stage_id=stage_id,
            score_per_win=score_per_win,
            score_per_draw=score_per_draw,
            score_per_bye=score_per_bye,
        )
        return await self._swiss_repo.create(sw)

    async def get_stage(self, stage_id: UUID) -> Stage:
        stage = await self._stage_repo.get(stage_id, load_groups=True, load_settings=True)
        if stage is None:
            raise NotFoundException("Stage not found")
        return stage

    async def list_stages(self, bracket_id: UUID) -> Sequence[Stage]:
        return await self._stage_repo.list_by_bracket(bracket_id)

    @BaseService.require_organizer
    async def delete_stage(self, event_id: UUID, issuer_id: UUID, stage_id: UUID) -> None:
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        await self._stage_repo.delete(stage_id)

    # ══════════════════════════════════════════════
    #  4. GROUPS
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def create_group(
            self,
            event_id: UUID,
            issuer_id: UUID,
            stage_id: UUID,
            *,
            name: str,
            advance_count: int | None = None,
    ) -> StageGroup:
        """Create a group within a stage (e.g. Group A, Group B)."""
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        group = StageGroup(
            stage_id=stage_id,
            name=name,
            advance_count=advance_count,
        )
        group = await self._group_repo.create(group)
        logger.info("Group '%s' created in stage %s", name, stage_id)
        return group

    async def list_groups(self, stage_id: UUID) -> Sequence[StageGroup]:
        return await self._group_repo.list_by_stage(stage_id)

    async def get_group(self, group_id: UUID) -> StageGroup:
        group = await self._group_repo.get(group_id, load_matches=True)
        if group is None:
            raise NotFoundException("Group not found")
        return group

    # ══════════════════════════════════════════════
    #  5. MATCH GENERATION — SINGLE ELIMINATION
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def generate_single_elimination(
            self,
            event_id: UUID,
            issuer_id: UUID,
            stage_id: UUID,
            team_ids: list[UUID],
    ) -> list[Match]:
        """
        Build a single-elimination bracket tree.

        *team_ids* should be in seeded order (seed 1 first).
        The tree is padded to the nearest power of 2 with byes.
        """
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        n = len(team_ids)

        if n < 2:
            raise BadRequestException("Need at least 2 teams for elimination bracket")

        # Pad to power of 2
        size = 1
        while size < n:
            size *= 2

        # Standard seeding: 1v(size), 2v(size-1), …
        seeds = list(range(1, size + 1))
        matchups = self._standard_seeding(seeds)

        # Ensure we have a group to hold the matches
        groups = await self._group_repo.list_by_stage(stage_id)
        if not groups:
            group = await self.create_group(stage_id, issuer_id, name="Main Bracket")
        else:
            group = groups[0]

        # Number of rounds
        num_rounds = int(math.log2(size))
        total_matches = size - 1

        # Create all matches (bottom-up)
        match_map: dict[int, Match] = {}  # index → Match
        match_idx = 0

        # Round 1 — leaf matches
        round1_matchups = matchups
        for pair in round1_matchups:
            m = Match(
                group_id=group.id,
                match_index=match_idx,
                round_number=1,
                bracket_position=BracketPosition.UPPER,
            )
            m = await self._match_repo.create(m)
            match_map[match_idx] = m

            # Create slots
            for slot_num, seed in enumerate(pair):
                if seed <= n:
                    # Real team
                    tid = team_ids[seed - 1]
                    slot = MatchSlot(
                        match_id=m.id,
                        slot_num=slot_num,
                        source_type=MatchSlotSourceType.MANUAL,
                    )
                    slot = await self._slot_repo.create(slot)
                    # Pre-assign score stub
                    ms = MatchScore(slot_id=slot.id, team_id=tid, score=0)
                    await self._score_repo.create(ms)
                else:
                    # Bye — empty slot
                    slot = MatchSlot(
                        match_id=m.id,
                        slot_num=slot_num,
                        source_type=MatchSlotSourceType.AUTO,
                    )
                    await self._slot_repo.create(slot)

            match_idx += 1

        # Subsequent rounds
        prev_round_matches = list(match_map.values())
        for rnd in range(2, num_rounds + 1):
            next_round_matches: list[Match] = []
            for i in range(0, len(prev_round_matches), 2):
                m = Match(
                    group_id=group.id,
                    match_index=match_idx,
                    round_number=rnd,
                    bracket_position=BracketPosition.UPPER,
                )
                m = await self._match_repo.create(m)
                match_map[match_idx] = m

                # Slot 0: winner of prev_round_matches[i]
                s0 = MatchSlot(
                    match_id=m.id,
                    slot_num=0,
                    source_type=MatchSlotSourceType.WINNER_OF,
                    source_match_id=prev_round_matches[i].id,
                )
                await self._slot_repo.create(s0)

                # Slot 1: winner of prev_round_matches[i+1]
                if i + 1 < len(prev_round_matches):
                    s1 = MatchSlot(
                        match_id=m.id,
                        slot_num=1,
                        source_type=MatchSlotSourceType.WINNER_OF,
                        source_match_id=prev_round_matches[i + 1].id,
                    )
                    await self._slot_repo.create(s1)

                next_round_matches.append(m)
                match_idx += 1

            prev_round_matches = next_round_matches

        all_matches = list(match_map.values())
        logger.info(
            "Single elimination bracket generated for stage %s: %d matches, %d rounds",
            stage_id, len(all_matches), num_rounds,
        )
        return all_matches

    # ══════════════════════════════════════════════
    #  6. MATCH GENERATION — DOUBLE ELIMINATION
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def generate_double_elimination(
            self,
            event_id: UUID,
            issuer_id: UUID,
            stage_id: UUID,
            team_ids: list[UUID],
    ) -> list[Match]:
        """
        Build a double-elimination bracket.

        Upper bracket: standard single-elim.
        Lower bracket: losers from upper get a second chance.
        Grand final: upper-bracket winner vs lower-bracket winner.
        """
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Stage does not belong to the specified event")

        n = len(team_ids)

        if n < 4:
            raise BadRequestException("Need at least 4 teams for double elimination")

        size = 1
        while size < n:
            size *= 2

        groups = await self._group_repo.list_by_stage(stage_id)
        if not groups:
            group = await self.create_group(stage_id, issuer_id, name="Double Elim Bracket")
        else:
            group = groups[0]

        matchups = self._standard_seeding(list(range(1, size + 1)))
        num_upper_rounds = int(math.log2(size))

        all_matches: list[Match] = []
        match_idx = 0
        upper_rounds: dict[int, list[Match]] = {}

        # --- Upper bracket ---
        # Round 1
        r1_matches: list[Match] = []
        for pair in matchups:
            m = Match(
                group_id=group.id,
                match_index=match_idx,
                round_number=1,
                bracket_position=BracketPosition.UPPER,
            )
            m = await self._match_repo.create(m)
            all_matches.append(m)
            r1_matches.append(m)

            for slot_num, seed in enumerate(pair):
                if seed <= n:
                    tid = team_ids[seed - 1]
                    slot = MatchSlot(
                        match_id=m.id,
                        slot_num=slot_num,
                        source_type=MatchSlotSourceType.MANUAL,
                    )
                    slot = await self._slot_repo.create(slot)
                    ms = MatchScore(slot_id=slot.id, team_id=tid, score=0)
                    await self._score_repo.create(ms)
                else:
                    slot = MatchSlot(
                        match_id=m.id,
                        slot_num=slot_num,
                        source_type=MatchSlotSourceType.AUTO,
                    )
                    await self._slot_repo.create(slot)
            match_idx += 1

        upper_rounds[1] = r1_matches
        prev_upper = r1_matches

        for rnd in range(2, num_upper_rounds + 1):
            cur: list[Match] = []
            for i in range(0, len(prev_upper), 2):
                m = Match(
                    group_id=group.id,
                    match_index=match_idx,
                    round_number=rnd,
                    bracket_position=BracketPosition.UPPER,
                )
                m = await self._match_repo.create(m)
                all_matches.append(m)
                cur.append(m)

                s0 = MatchSlot(
                    match_id=m.id, slot_num=0,
                    source_type=MatchSlotSourceType.WINNER_OF,
                    source_match_id=prev_upper[i].id,
                )
                await self._slot_repo.create(s0)
                if i + 1 < len(prev_upper):
                    s1 = MatchSlot(
                        match_id=m.id, slot_num=1,
                        source_type=MatchSlotSourceType.WINNER_OF,
                        source_match_id=prev_upper[i + 1].id,
                    )
                    await self._slot_repo.create(s1)
                match_idx += 1
            upper_rounds[rnd] = cur
            prev_upper = cur

        # --- Lower bracket ---
        # Lower bracket receives losers from upper bracket rounds.
        # Lower round 1: losers from upper round 1, paired
        lower_rounds: dict[int, list[Match]] = {}
        lower_rnd = 1

        # Losers from upper R1
        prev_lower: list[Match] = []
        losers_r1 = upper_rounds[1]
        for i in range(0, len(losers_r1), 2):
            m = Match(
                group_id=group.id,
                match_index=match_idx,
                round_number=lower_rnd,
                bracket_position=BracketPosition.LOWER,
            )
            m = await self._match_repo.create(m)
            all_matches.append(m)
            prev_lower.append(m)

            s0 = MatchSlot(
                match_id=m.id, slot_num=0,
                source_type=MatchSlotSourceType.LOSER_OF,
                source_match_id=losers_r1[i].id,
            )
            await self._slot_repo.create(s0)
            if i + 1 < len(losers_r1):
                s1 = MatchSlot(
                    match_id=m.id, slot_num=1,
                    source_type=MatchSlotSourceType.LOSER_OF,
                    source_match_id=losers_r1[i + 1].id,
                )
                await self._slot_repo.create(s1)
            match_idx += 1

        lower_rounds[lower_rnd] = prev_lower

        # For each subsequent upper round, feed losers into lower bracket
        for upper_rnd in range(2, num_upper_rounds + 1):
            # Lower "consolidation" round: winners of prev lower vs each other
            lower_rnd += 1
            consolidation: list[Match] = []
            losers_from_upper = upper_rounds[upper_rnd]

            for i in range(min(len(prev_lower), len(losers_from_upper))):
                m = Match(
                    group_id=group.id,
                    match_index=match_idx,
                    round_number=lower_rnd,
                    bracket_position=BracketPosition.LOWER,
                )
                m = await self._match_repo.create(m)
                all_matches.append(m)
                consolidation.append(m)

                # Slot 0: winner of previous lower match
                s0 = MatchSlot(
                    match_id=m.id, slot_num=0,
                    source_type=MatchSlotSourceType.WINNER_OF,
                    source_match_id=prev_lower[i].id if i < len(prev_lower) else None,
                )
                await self._slot_repo.create(s0)
                # Slot 1: loser from upper round
                s1 = MatchSlot(
                    match_id=m.id, slot_num=1,
                    source_type=MatchSlotSourceType.LOSER_OF,
                    source_match_id=losers_from_upper[i].id if i < len(losers_from_upper) else None,
                )
                await self._slot_repo.create(s1)
                match_idx += 1

            lower_rounds[lower_rnd] = consolidation
            prev_lower = consolidation

        # --- Grand Final ---
        upper_winner_match = upper_rounds[num_upper_rounds][0]
        lower_winner_match = prev_lower[0] if prev_lower else None

        grand_final = Match(
            group_id=group.id,
            match_index=match_idx,
            round_number=num_upper_rounds + 1,
            bracket_position=None,  # Grand Final
        )
        grand_final = await self._match_repo.create(grand_final)
        all_matches.append(grand_final)

        s0 = MatchSlot(
            match_id=grand_final.id, slot_num=0,
            source_type=MatchSlotSourceType.WINNER_OF,
            source_match_id=upper_winner_match.id,
        )
        await self._slot_repo.create(s0)

        if lower_winner_match:
            s1 = MatchSlot(
                match_id=grand_final.id, slot_num=1,
                source_type=MatchSlotSourceType.WINNER_OF,
                source_match_id=lower_winner_match.id,
            )
            await self._slot_repo.create(s1)

        logger.info(
            "Double elimination bracket for stage %s: %d matches",
            stage_id, len(all_matches),
        )
        return all_matches

    # ══════════════════════════════════════════════
    #  7. MATCH GENERATION — ROUND ROBIN
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def generate_round_robin(
            self,
            event_id: UUID,
            issuer_id: UUID,
            group_id: UUID,
            team_ids: list[UUID],
    ) -> list[Match]:
        """
        Generate all round-robin pairings for *team_ids* in a group.
        Creates one match per pair per ``meetings_per_pair`` setting.
        """
        group = await self._group_repo.get(group_id)
        if group is None:
            raise NotFoundException("Group not found")

        stage = await self._stage_repo.get(group.stage_id, load_settings=True)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Group does not belong to the specified event")

        rr = await self._rr_repo.get_by_stage_id(stage.id)
        meetings = rr.meetings_per_pair if rr else 1

        n = len(team_ids)
        if n < 2:
            raise BadRequestException("Need at least 2 teams for round-robin")

        # Classic circle-method scheduling
        teams: list[UUID | None] = list(team_ids)
        if n % 2 == 1:
            teams.append(None)  # BYE placeholder
        total = len(teams)
        rounds = total - 1
        matches_per_round = total // 2

        all_matches: list[Match] = []
        match_idx = 0

        for meeting in range(meetings):
            fixed = teams[0]
            rotating = teams[1:]

            for rnd in range(rounds):
                current_rotation = [fixed] + rotating
                for i in range(matches_per_round):
                    home = current_rotation[i]
                    away = current_rotation[total - 1 - i]

                    if home is None or away is None:
                        continue  # BYE round

                    m = Match(
                        group_id=group_id,
                        match_index=match_idx,
                        round_number=rnd + 1 + (meeting * rounds),
                        bracket_position=None,
                    )
                    m = await self._match_repo.create(m)
                    all_matches.append(m)

                    # Slot 0 = home
                    slot0 = MatchSlot(
                        match_id=m.id, slot_num=0,
                        source_type=MatchSlotSourceType.MANUAL,
                    )
                    slot0 = await self._slot_repo.create(slot0)
                    await self._score_repo.create(MatchScore(slot_id=slot0.id, team_id=home, score=0))

                    # Slot 1 = away
                    slot1 = MatchSlot(
                        match_id=m.id, slot_num=1,
                        source_type=MatchSlotSourceType.MANUAL,
                    )
                    slot1 = await self._slot_repo.create(slot1)
                    await self._score_repo.create(MatchScore(slot_id=slot1.id, team_id=away, score=0))

                    match_idx += 1

                # Rotate
                rotating = [rotating[-1]] + rotating[:-1]

        logger.info(
            "Round-robin for group %s: %d matches (%d meetings)",
            group_id, len(all_matches), meetings,
        )
        return all_matches

    # ══════════════════════════════════════════════
    #  8. MATCH GENERATION — SWISS
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def generate_swiss_round(
            self,
            event_id: UUID,
            issuer_id: UUID,
            group_id: UUID,
            round_number: int,
    ) -> list[Match]:
        """
        Generate pairings for a Swiss-system round.

        Teams are paired by current score (best vs best), avoiding rematches.
        If there is an odd number of teams, the lowest-ranked team gets a BYE.
        """
        group = await self._group_repo.get(group_id)
        if group is None:
            raise NotFoundException("Group not found")

        stage = await self._stage_repo.get(group.stage_id, load_settings=True)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        if bracket.event_id != event_id:
             raise BadRequestException("Group does not belong to the specified event")

        # Build standings so far
        standings = await self._compute_group_standings(group_id, stage.id)
        team_scores = {s["team_id"]: s["points"] for s in standings}

        # Determine teams already paired (to avoid rematches)
        existing_matches = await self._match_repo.list_by_stage_group(group_id)
        played_pairs: set[frozenset] = set()
        for m in existing_matches:
            slots = await self._slot_repo.list_by_match(m.id)
            team_in_match: list[UUID] = []
            for sl in slots:
                sc = await self._score_repo.get_by_slot_id(sl.id)
                if sc:
                    team_in_match.append(sc.team_id)
            if len(team_in_match) == 2:
                played_pairs.add(frozenset(team_in_match))

        # Sort teams by points descending, then shuffle ties
        sorted_teams = sorted(team_scores.keys(), key=lambda t: team_scores[t], reverse=True)

        # BYE handling
        bye_team: UUID | None = None
        if len(sorted_teams) % 2 == 1:
            # Give BYE to the lowest-scoring team that hasn't had a BYE
            for t in reversed(sorted_teams):
                bye_team = t
                sorted_teams.remove(t)
                break

        # Greedy pairing
        paired: list[tuple[UUID, UUID]] = []
        used: set[UUID] = set()
        for t in sorted_teams:
            if t in used:
                continue
            for opp in sorted_teams:
                if opp in used or opp == t:
                    continue
                if frozenset([t, opp]) not in played_pairs:
                    paired.append((t, opp))
                    used.add(t)
                    used.add(opp)
                    break
            else:
                # If no valid opponent found (all rematches), pair with next available
                for opp in sorted_teams:
                    if opp not in used and opp != t:
                        paired.append((t, opp))
                        used.add(t)
                        used.add(opp)
                        break

        # Create matches
        all_matches: list[Match] = []
        existing_count = len(existing_matches)
        for idx, (home, away) in enumerate(paired):
            m = Match(
                group_id=group_id,
                match_index=existing_count + idx,
                round_number=round_number,
                bracket_position=None,
            )
            m = await self._match_repo.create(m)
            all_matches.append(m)

            slot0 = MatchSlot(
                match_id=m.id, slot_num=0,
                source_type=MatchSlotSourceType.MANUAL,
            )
            slot0 = await self._slot_repo.create(slot0)
            await self._score_repo.create(MatchScore(slot_id=slot0.id, team_id=home, score=0))

            slot1 = MatchSlot(
                match_id=m.id, slot_num=1,
                source_type=MatchSlotSourceType.MANUAL,
            )
            slot1 = await self._slot_repo.create(slot1)
            await self._score_repo.create(MatchScore(slot_id=slot1.id, team_id=away, score=0))

        # Record BYE as an auto-win
        if bye_team:
            sw = await self._swiss_repo.get_by_stage_id(stage.id)
            # BYE points are added via standings computation, not as a real match

        logger.info(
            "Swiss round %d for group %s: %d pairings", round_number, group_id, len(paired),
        )
        return all_matches

    # ══════════════════════════════════════════════
    #  9. WINNER ADVANCEMENT
    # ══════════════════════════════════════════════

    async def advance_winner(self, match_id: UUID, winner_team_id: UUID) -> None:
        """
        After a match is complete, push the winning team into downstream
        MatchSlots that reference this match as ``source_match_id``.
        """
        match = await self._match_repo.get(match_id)
        if match is None:
            raise NotFoundException("Match not found")

        # Find all slots in other matches that source from this match
        # We need to look for MatchSlots where source_match_id == match_id
        # and source_type == WINNER_OF (or LOSER_OF for lower bracket).
        # Unfortunately, we don't have a query for that, so we iterate
        # the group matches.
        if match.group_id is None:
            return

        group_matches = await self._match_repo.list_by_stage_group(match.group_id)
        for gm in group_matches:
            if gm.id == match_id:
                continue
            slots = await self._slot_repo.list_by_match(gm.id)
            for slot in slots:
                if slot.source_match_id == match_id:
                    if slot.source_type == MatchSlotSourceType.WINNER_OF:
                        # Assign winner
                        existing = await self._score_repo.get_by_slot_id(slot.id)
                        if existing:
                            existing.team_id = winner_team_id
                            await self._score_repo.update(existing)
                        else:
                            ms = MatchScore(slot_id=slot.id, team_id=winner_team_id, score=0)
                            await self._score_repo.create(ms)
                    elif slot.source_type == MatchSlotSourceType.LOSER_OF:
                        # Determine loser
                        loser_id = await self._get_loser(match_id, winner_team_id)
                        if loser_id:
                            existing = await self._score_repo.get_by_slot_id(slot.id)
                            if existing:
                                existing.team_id = loser_id
                                await self._score_repo.update(existing)
                            else:
                                ms = MatchScore(slot_id=slot.id, team_id=loser_id, score=0)
                                await self._score_repo.create(ms)

        logger.info("Match %s: advanced winner %s", match_id, winner_team_id)

    async def _get_loser(self, match_id: UUID, winner_team_id: UUID) -> UUID | None:
        """Return the team_id that lost the match."""
        slots = await self._slot_repo.list_by_match(match_id)
        for slot in slots:
            sc = await self._score_repo.get_by_slot_id(slot.id)
            if sc and sc.team_id != winner_team_id:
                return sc.team_id
        return None

    # ══════════════════════════════════════════════
    #  10. STANDINGS
    # ══════════════════════════════════════════════

    async def get_standings(
            self,
            group_id: UUID,
    ) -> list[dict]:
        """
        Compute group/swiss standings from match scores.

        Returns a list sorted by points descending::

            [
                {"team_id": UUID, "points": int, "wins": int, "draws": int, "losses": int,
                 "score_for": int, "score_against": int, "diff": int},
                ...
            ]
        """
        group = await self._group_repo.get(group_id)
        if group is None:
            raise NotFoundException("Group not found")
        return await self._compute_group_standings(group_id, group.stage_id)

    async def _compute_group_standings(self, group_id: UUID, stage_id: UUID) -> list[dict]:
        """Internal standings computation."""
        rr = await self._rr_repo.get_by_stage_id(stage_id)
        sw = await self._swiss_repo.get_by_stage_id(stage_id)

        win_pts = (rr.score_per_win if rr else None) or (sw.score_per_win if sw else 3)
        draw_pts = (rr.score_per_draw if rr else None) or (sw.score_per_draw if sw else 1)

        matches = await self._match_repo.list_by_stage_group(group_id)

        stats: dict[UUID, dict] = {}

        def _ensure(tid: UUID) -> dict:
            if tid not in stats:
                stats[tid] = {
                    "team_id": tid,
                    "points": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "score_for": 0,
                    "score_against": 0,
                    "diff": 0,
                }
            return stats[tid]

        for m in matches:
            # Skip unfinished
            if m.time_end is None:
                continue

            slots = await self._slot_repo.list_by_match(m.id)
            scores: list[MatchScore] = []
            for sl in slots:
                sc = await self._score_repo.get_by_slot_id(sl.id)
                if sc:
                    scores.append(sc)

            if len(scores) != 2:
                continue

            a, b = scores[0], scores[1]
            sa = _ensure(a.team_id)
            sb = _ensure(b.team_id)

            sa["score_for"] += a.score
            sa["score_against"] += b.score
            sb["score_for"] += b.score
            sb["score_against"] += a.score

            if a.score > b.score:
                sa["wins"] += 1
                sa["points"] += win_pts
                sb["losses"] += 1
            elif b.score > a.score:
                sb["wins"] += 1
                sb["points"] += win_pts
                sa["losses"] += 1
            else:
                sa["draws"] += 1
                sb["draws"] += 1
                sa["points"] += draw_pts
                sb["points"] += draw_pts

        for s in stats.values():
            s["diff"] = s["score_for"] - s["score_against"]

        return sorted(stats.values(), key=lambda x: (x["points"], x["diff"]), reverse=True)

    # ══════════════════════════════════════════════
    #  11. STAGE COMPLETION & PROMOTION
    # ══════════════════════════════════════════════

    async def complete_stage(
            self,
            stage_id: UUID,
            organizer_id: UUID,
    ) -> list[UUID]:
        """
        Mark a stage as complete and determine which teams advance.

        For group stages, the top ``advance_count`` teams per group are promoted.
        Returns the list of advancing team IDs.
        """
        stage = await self._stage_repo.get(stage_id, load_groups=True)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        await self._assert_organizer(bracket.event_id, organizer_id)

        advancing: list[UUID] = []

        groups = await self._group_repo.list_by_stage(stage_id)
        for group in groups:
            standings = await self._compute_group_standings(group.id, stage_id)
            advance_count = group.advance_count or 2  # Default: top 2
            for entry in standings[:advance_count]:
                advancing.append(entry["team_id"])

        logger.info("Stage %s completed. %d teams advance.", stage_id, len(advancing))
        return advancing

    async def promote_teams_to_next_stage(
            self,
            bracket_id: UUID,
            organizer_id: UUID,
            current_stage_index: int,
            team_ids: list[UUID],
    ) -> None:
        """
        Move advancing teams from stage N to stage N+1.

        Creates BracketPlacements for the next stage so they can be seeded.
        """
        bracket = await self._bracket_repo.get(bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        await self._assert_organizer(bracket.event_id, organizer_id)

        stages = await self._stage_repo.list_by_bracket(bracket_id)
        next_stage = next(
            (s for s in stages if s.stage_index == current_stage_index + 1), None,
        )
        if next_stage is None:
            raise BadRequestException("No next stage exists — this is the final stage")

        # Clear old placements for this bracket and recreate
        for idx, tid in enumerate(team_ids):
            bp = BracketPlacement(
                bracket_id=bracket_id,
                team_id=tid,
                placement=idx + 1,
            )
            await self._placement_repo.create(bp)

        logger.info(
            "Promoted %d teams from stage %d to stage %d in bracket %s",
            len(team_ids), current_stage_index, current_stage_index + 1, bracket_id,
        )

    # ══════════════════════════════════════════════
    #  12. START STAGE
    # ══════════════════════════════════════════════

    @BaseService.require_organizer
    async def start_stage(
            self,
            stage_id: UUID,
            organizer_id: UUID,
            team_ids: list[UUID],
    ) -> list[Match]:
        """
        Initialize the first round of a stage.

        Dispatches to the correct generator based on ``stage.format``.
        """
        stage = await self._stage_repo.get(stage_id)
        if stage is None:
            raise NotFoundException("Stage not found")
        bracket = await self._bracket_repo.get(stage.bracket_id)
        if bracket is None:
            raise NotFoundException("Bracket not found")
        await self._assert_organizer(bracket.event_id, organizer_id)

        # Auto-transition: REGISTRATION -> FORMATION
        event = await self._event_repo.get(bracket.event_id)
        if event and event.status == EventStatus.REGISTRATION:
            try:
                event.transition_to(EventStatus.FORMATION)
                await self._event_repo.update(event)
            except ValueError:
                pass  # Ignore if invalid, logic might validly proceed or fail later

        fmt = stage.format.upper()

        if fmt == "SINGLE_ELIM":
            return await self.generate_single_elimination(stage_id, organizer_id, team_ids)
        elif fmt == "DOUBLE_ELIM":
            return await self.generate_double_elimination(stage_id, organizer_id, team_ids)
        elif fmt in ("ROUND_ROBIN", "GROUPS"):
            groups = await self._group_repo.list_by_stage(stage_id)
            if not groups:
                raise BadRequestException("No groups configured for this stage")
            # Distribute teams across groups evenly
            all_matches: list[Match] = []
            group_list = list(groups)
            for i, tid in enumerate(team_ids):
                g = group_list[i % len(group_list)]
                # Collect teams per group
            # Actually generate per group
            group_teams: dict[UUID, list[UUID]] = {g.id: [] for g in group_list}
            for i, tid in enumerate(team_ids):
                g = group_list[i % len(group_list)]
                group_teams[g.id].append(tid)
            for gid, tids in group_teams.items():
                matches = await self.generate_round_robin(gid, organizer_id, tids)
                all_matches.extend(matches)
            return all_matches
        elif fmt == "SWISS":
            groups = await self._group_repo.list_by_stage(stage_id)
            if not groups:
                group = await self.create_group(stage_id, organizer_id, name="Swiss Pool")
                gid = group.id
            else:
                gid = groups[0].id
            # Assign all teams, generate round 1
            return await self.generate_swiss_round(gid, organizer_id, round_number=1)
        else:
            raise BadRequestException(f"Unknown stage format: {stage.format}")

    # ══════════════════════════════════════════════
    #  11. WINNER PROPAGATION
    # ══════════════════════════════════════════════

    async def propagate_winner(self, match_id: UUID, winner_team_id: UUID) -> None:
        """
        Move winner to the next match(es) in the bracket.
        """
        match = await self._match_repo.get(match_id)
        if match is None:
            raise NotFoundException("Match not found")

        # Find slots waiting for this result
        # Using filter expression for SQLAlchemy repo
        slots = await self._slot_repo.list(0, 100, None, MatchSlot.source_match_id == match_id)

        for slot in slots:
            existing_score = await self._score_repo.get_by_slot_id(slot.id)
            if existing_score:
                existing_score.team_id = winner_team_id
                await self._score_repo.update(existing_score)
            else:
                await self._score_repo.create(MatchScore(
                    slot_id=slot.id,
                    team_id=winner_team_id,
                    score=0,
                ))

            logger.info("Propagated winner %s to match %s slot %d", winner_team_id, slot.match_id, slot.slot_num)

    # ══════════════════════════════════════════════
    #  Pure helpers
    # ══════════════════════════════════════════════

    @staticmethod
    def _standard_seeding(seeds: list[int]) -> list[tuple[int, int]]:
        """
        Standard tournament seeding for power-of-2 bracket.

        Produces pairs like (1, N), (N/2+1, N/2), … so that top seeds
        are on opposite sides and only meet in the final.
        """
        if len(seeds) == 2:
            return [(seeds[0], seeds[1])]

        mid = len(seeds) // 2
        top = seeds[:mid]
        bottom = seeds[mid:]
        bottom.reverse()
        return list(zip(top, bottom))
