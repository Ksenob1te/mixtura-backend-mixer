"""
DraftService — transforms an approved player pool into balanced teams.

Strategies:
  • RANDOM  — simple shuffle & deal
  • BALANCE — greedy snake-draft by MMR
  • MANUAL  — empty team shells, organizer fills by hand

Flow: ``initialize → generate_teams → (reroll | swap | move | pin) → finalize``
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from src.infra.postgre.exceptions import IntegrityUniqueException
from src.infra.postgre.models import (
    Draft,
    DraftedPlayer,
    EventPlayer,
    Team,
    TeamPlayer,
)
from src.infra.postgre.models.draft import DraftStatus
from src.infra.postgre.models.event import TeamFormation
from src.infra.postgre.repo import (
    DraftRepository,
    DraftedPlayerRepository,
    EventRepository,
    OrganizerRepository,
    PlayerRepository,
    PlayerRoleRepository,
    SelectedGameRoleRepository,
    TeamPlayerRepository,
    TeamRepository,
)
from ._base import BaseService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _PlayerInfo:
    """Lightweight snapshot used during team-building algorithms."""

    event_player_id: UUID
    member_id: UUID
    rating: float = 0.0
    role_ids: list[UUID] = field(default_factory=list)
    is_pinned: bool = False


class DraftService(BaseService):
    """Transforms a pool of EventPlayers into Teams via configurable strategies."""

    def __init__(
        self,
        draft_repo: DraftRepository,
        drafted_player_repo: DraftedPlayerRepository,
        player_repo: PlayerRepository,
        player_role_repo: PlayerRoleRepository,
        team_repo: TeamRepository,
        team_player_repo: TeamPlayerRepository,
        event_repo: EventRepository,
        organizer_repo: OrganizerRepository,
        game_role_repo: SelectedGameRoleRepository,
    ) -> None:
        self._draft_repo = draft_repo
        self._dp_repo = drafted_player_repo
        self._player_repo = player_repo
        self._player_role_repo = player_role_repo
        self._team_repo = team_repo
        self._tp_repo = team_player_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._game_role_repo = game_role_repo

    # ── private helpers ──────────────────────────

    async def _get_draft_or_404(self, draft_id: UUID, *, load_players: bool = False) -> Draft:
        draft = await self._draft_repo.get(draft_id, load_drafted_players=load_players)
        if draft is None:
            raise NotFoundException("Draft not found")
        return draft

    async def _assert_draft_mutable(self, draft: Draft) -> None:
        if draft.status == DraftStatus.COMPLETED:
            raise ConflictException("Draft has already been finalized")

    async def _get_event_for_draft(self, draft: Draft):
        event = await self._event_repo.get(draft.event_id)
        if event is None:
            raise NotFoundException("Event not found")
        return event

    async def _resolve_default_role_id(self, event_id: UUID) -> UUID | None:
        roles = await self._game_role_repo.list_by_event(event_id)
        return roles[0].id if roles else None

    async def _delete_draft_teams(self, draft_id: UUID, event_id: UUID) -> None:
        """Remove all teams linked to this draft."""
        teams = await self._team_repo.list_by_event(event_id)
        for t in teams:
            if t.draft_id == draft_id:
                await self._team_repo.delete(t.id)

    async def _build_player_infos(self, draft_id: UUID, event_id: UUID) -> list[_PlayerInfo]:
        """Build a lightweight snapshot of all drafted players with their roles."""
        all_dp = await self._dp_repo.list_by_draft(draft_id)
        # Single query with roles pre-loaded
        players = await self._player_repo.list_by_event_with_roles(event_id)
        player_map = {p.id: p for p in players}

        infos: list[_PlayerInfo] = []
        for dp in all_dp:
            ep = player_map.get(dp.event_player_id)
            if ep is None:
                continue
            infos.append(_PlayerInfo(
                event_player_id=ep.id,
                member_id=ep.member_id,
                rating=0.0,  # TODO: fetch from rating-set via RPC
                role_ids=[r.game_role_id for r in ep.player_roles],
                is_pinned=ep.is_draft_pinned,
            ))
        return infos

    # ── initialize ───────────────────────────────

    async def initialize_draft(self, event_id: UUID, organizer_id: UUID) -> Draft:
        """
        Freeze the approved player pool and open a new Draft session.

        Creates a DraftedPlayer snapshot for every EventPlayer.
        """
        event = await self._fetch_event(event_id)
        await self._assert_organizer(event_id, organizer_id)

        existing = await self._draft_repo.list_by_event(event_id)
        open_drafts = [d for d in existing if d.status != DraftStatus.COMPLETED]
        if open_drafts and not event.allow_multiple_drafts:
            raise ConflictException("An open draft already exists for this event")

        players = await self._player_repo.list_by_event(event_id)
        if len(players) < event.team_size:
            raise BadRequestException(
                f"Not enough players ({len(players)}) for teams of {event.team_size}",
            )

        draft = await self._draft_repo.create(Draft(event_id=event_id, status=DraftStatus.OPEN))

        for ep in players:
            await self._dp_repo.create(DraftedPlayer(
                draft_id=draft.id,
                event_player_id=ep.id,
                is_captain=None,
            ))

        logger.info("Draft %s initialized for event %s (%d players)", draft.id, event_id, len(players))
        return draft

    # ── generate teams ───────────────────────────

    async def generate_teams(
        self,
        draft_id: UUID,
        organizer_id: UUID,
        *,
        method: str | None = None,
    ) -> list[Team]:
        """
        Distribute drafted players into teams **and persist TeamPlayer rows**.

        This method is idempotent: calling it again (reroll) deletes previous
        draft teams and regenerates from scratch.
        """
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        event = await self._get_event_for_draft(draft)
        await self._assert_organizer(event.id, organizer_id)

        formation = TeamFormation(method) if method else event.team_formation
        team_size = event.team_size

        infos = await self._build_player_infos(draft_id, event.id)
        if len(infos) < team_size:
            raise BadRequestException("Not enough players to form even one team")

        num_teams = len(infos) // team_size

        # Clean up previous attempt (reroll)
        await self._delete_draft_teams(draft_id, event.id)

        # Distribute into buckets
        if formation == TeamFormation.BALANCE:
            buckets = self._balance_mmr(infos, team_size, num_teams)
        elif formation == TeamFormation.MANUAL:
            buckets = [[] for _ in range(num_teams)]
        else:
            buckets = self._shuffle_deal(infos, team_size, num_teams)

        # Resolve a default game role for TeamPlayer rows
        default_role_id = await self._resolve_default_role_id(event.id)

        # Persist teams + TeamPlayer rows
        created: list[Team] = []
        for idx, bucket in enumerate(buckets):
            team = await self._team_repo.create(Team(
                event_id=event.id, draft_id=draft_id, name=f"Team {idx + 1}",
            ))
            created.append(team)

            for rank, pi in enumerate(bucket):
                if default_role_id is not None:
                    await self._tp_repo.create(TeamPlayer(
                        team_id=team.id,
                        member_id=pi.member_id,
                        game_role_id=default_role_id,
                        rating=pi.rating,
                    ))
                # Mark first player in each bucket as captain
                if rank == 0:
                    dp_list = await self._dp_repo.list_by_draft(draft_id)
                    dp = next((d for d in dp_list if d.event_player_id == pi.event_player_id), None)
                    if dp is not None:
                        dp.is_captain = True
                        await self._dp_repo.update(dp)

        draft.status = DraftStatus.BALANCE_SELECTED
        await self._draft_repo.update(draft)

        logger.info("Draft %s: %d teams via %s", draft_id, len(created), formation.value)
        return created

    # ── reroll ───────────────────────────────────

    async def reroll(self, draft_id: UUID, organizer_id: UUID) -> list[Team]:
        """Discard current team assignments and re-run generation."""
        return await self.generate_teams(draft_id, organizer_id)

    # ── manual swap ──────────────────────────────

    async def manual_swap(
        self,
        draft_id: UUID,
        organizer_id: UUID,
        player_a_member_id: UUID,
        player_b_member_id: UUID,
    ) -> None:
        """Swap two players between their draft teams."""
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        event = await self._get_event_for_draft(draft)
        await self._assert_organizer(event.id, organizer_id)

        teams = await self._team_repo.list_by_event(event.id)
        draft_teams = {t.id: t for t in teams if t.draft_id == draft_id}

        tp_a: TeamPlayer | None = None
        tp_b: TeamPlayer | None = None
        for team_id in draft_teams:
            for tp in await self._tp_repo.list_by_team(team_id):
                if tp.member_id == player_a_member_id:
                    tp_a = tp
                elif tp.member_id == player_b_member_id:
                    tp_b = tp

        if tp_a is None or tp_b is None:
            raise NotFoundException("One or both players not found in draft teams")
        if tp_a.team_id == tp_b.team_id:
            raise BadRequestException("Both players are already on the same team")

        tp_a.team_id, tp_b.team_id = tp_b.team_id, tp_a.team_id
        await self._tp_repo.update(tp_a)
        await self._tp_repo.update(tp_b)
        logger.info("Draft %s: swapped %s ↔ %s", draft_id, player_a_member_id, player_b_member_id)

    # ── move player ──────────────────────────────

    async def move_player(
        self,
        draft_id: UUID,
        organizer_id: UUID,
        member_id: UUID,
        target_team_id: UUID,
    ) -> None:
        """Move a player from their current draft team to *target_team_id*."""
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        event = await self._get_event_for_draft(draft)
        await self._assert_organizer(event.id, organizer_id)

        teams = await self._team_repo.list_by_event(event.id)
        draft_team_ids = {t.id for t in teams if t.draft_id == draft_id}

        if target_team_id not in draft_team_ids:
            raise NotFoundException("Target team not found in this draft")

        tp_found: TeamPlayer | None = None
        for tid in draft_team_ids:
            for tp in await self._tp_repo.list_by_team(tid):
                if tp.member_id == member_id:
                    tp_found = tp
                    break
            if tp_found:
                break

        if tp_found is None:
            raise NotFoundException("Player not found in any draft team")

        tp_found.team_id = target_team_id
        await self._tp_repo.update(tp_found)
        logger.info("Draft %s: moved %s → team %s", draft_id, member_id, target_team_id)

    # ── pin / unpin ──────────────────────────────

    async def pin_player(
        self,
        draft_id: UUID,
        organizer_id: UUID,
        event_player_id: UUID,
        pinned: bool = True,
    ) -> EventPlayer:
        """Pin a player so they survive rerolls."""
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        await self._assert_organizer(draft.event_id, organizer_id)

        player = await self._player_repo.get(event_player_id)
        if player is None:
            raise NotFoundException("EventPlayer not found")

        player.is_draft_pinned = pinned
        return await self._player_repo.update(player)

    # ── captain ──────────────────────────────────

    async def set_captain(
        self,
        draft_id: UUID,
        organizer_id: UUID,
        event_player_id: UUID,
        is_captain: bool = True,
    ) -> DraftedPlayer:
        """Set (or unset) the captain flag for a drafted player."""
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        await self._assert_organizer(draft.event_id, organizer_id)

        all_dp = await self._dp_repo.list_by_draft(draft_id)
        dp = next((d for d in all_dp if d.event_player_id == event_player_id), None)
        if dp is None:
            raise NotFoundException("DraftedPlayer not found")

        # If promoting to captain, demote the current captain on the same team
        if is_captain:
            player = await self._player_repo.get(event_player_id)
            if player is None:
                raise NotFoundException("EventPlayer not found")

            teams = await self._team_repo.list_by_event(draft.event_id)
            for team in teams:
                if team.draft_id != draft_id:
                    continue
                tp_list = await self._tp_repo.list_by_team(team.id)
                if any(tp.member_id == player.member_id for tp in tp_list):
                    # Found the team — demote existing captain
                    team_member_ids = {tp.member_id for tp in tp_list}
                    player_map = await self._player_repo.list_by_event(draft.event_id)
                    ep_by_member = {p.member_id: p.id for p in player_map}
                    for other_dp in all_dp:
                        if other_dp.id == dp.id or not other_dp.is_captain:
                            continue
                        other_ep_id = other_dp.event_player_id
                        other_member = next(
                            (mid for mid, eid in ep_by_member.items() if eid == other_ep_id),
                            None,
                        )
                        if other_member in team_member_ids:
                            other_dp.is_captain = False
                            await self._dp_repo.update(other_dp)
                    break

        dp.is_captain = is_captain
        return await self._dp_repo.update(dp)

    # ── finalize ─────────────────────────────────

    async def finalize_draft(self, draft_id: UUID, organizer_id: UUID) -> list[Team]:
        """
        Commit the draft.

        Marks the draft as COMPLETED. TeamPlayer rows already exist
        from ``generate_teams``, so this is purely a status transition.
        """
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        event = await self._get_event_for_draft(draft)
        await self._assert_organizer(event.id, organizer_id)

        teams = await self._team_repo.list_by_event(event.id)
        draft_teams = [t for t in teams if t.draft_id == draft_id]

        if not draft_teams:
            raise BadRequestException("No teams generated yet — call generate_teams first")

        # Validate that every team has players (unless MANUAL mode)
        for team in draft_teams:
            roster = await self._tp_repo.list_by_team(team.id)
            if not roster and event.team_formation != TeamFormation.MANUAL:
                raise BadRequestException(f"Team '{team.name}' has no players assigned")

        draft.status = DraftStatus.COMPLETED
        await self._draft_repo.update(draft)
        logger.info("Draft %s finalized with %d teams", draft_id, len(draft_teams))
        return draft_teams

    # ── read helpers ─────────────────────────────

    async def get_draft(self, draft_id: UUID) -> Draft:
        return await self._get_draft_or_404(draft_id, load_players=True)

    async def list_drafts(self, event_id: UUID) -> Sequence[Draft]:
        return await self._draft_repo.list_by_event(event_id)

    async def get_draft_players(self, draft_id: UUID) -> Sequence[DraftedPlayer]:
        return await self._dp_repo.list_by_draft(draft_id)

    async def get_draft_teams(self, draft_id: UUID) -> list[Team]:
        draft = await self._get_draft_or_404(draft_id)
        teams = await self._team_repo.list_by_event(draft.event_id)
        return [t for t in teams if t.draft_id == draft_id]

    # ── cancel ───────────────────────────────────

    async def cancel_draft(self, draft_id: UUID, organizer_id: UUID) -> None:
        """Delete a draft and its teams (only if not yet finalized)."""
        draft = await self._get_draft_or_404(draft_id)
        await self._assert_draft_mutable(draft)
        await self._assert_organizer(draft.event_id, organizer_id)

        await self._delete_draft_teams(draft_id, draft.event_id)
        await self._draft_repo.delete(draft_id)
        logger.info("Draft %s cancelled", draft_id)

    # ── balancing algorithms (pure) ──────────────

    @staticmethod
    def _shuffle_deal(
        infos: list[_PlayerInfo], team_size: int, num_teams: int,
    ) -> list[list[_PlayerInfo]]:
        """Shuffle and deal round-robin into *num_teams* buckets."""
        pool = list(infos)
        random.shuffle(pool)
        buckets: list[list[_PlayerInfo]] = [[] for _ in range(num_teams)]
        for i, p in enumerate(pool[: num_teams * team_size]):
            buckets[i % num_teams].append(p)
        return buckets

    @staticmethod
    def _balance_mmr(
        infos: list[_PlayerInfo], team_size: int, num_teams: int,
    ) -> list[list[_PlayerInfo]]:
        """Greedy snake-draft: assign the best available to the weakest team."""
        pool = sorted(infos, key=lambda p: p.rating, reverse=True)
        buckets: list[list[_PlayerInfo]] = [[] for _ in range(num_teams)]
        sums = [0.0] * num_teams
        for p in pool[: num_teams * team_size]:
            target = min(range(num_teams), key=lambda i: sums[i])
            buckets[target].append(p)
            sums[target] += p.rating
        return buckets

