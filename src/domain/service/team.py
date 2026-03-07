"""
TeamService — post-draft team management.

Covers roster changes, captaincy, premade-team registration (for
tournaments that accept pre-formed squads), and team queries.

Premade flow:   register_premade_team → rename / roster edits → …
Draft flow:     DraftService finalizes → rename / roster edits → …
"""

from __future__ import annotations

import logging
from typing import Sequence
from uuid import UUID

from src.domain.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from src.infra.postgre.exceptions import IntegrityUniqueException
from src.infra.postgre.models import (
    Team,
    TeamPlayer,
)
from src.infra.postgre.repo import (
    DraftedPlayerRepository,
    EventRepository,
    OrganizerRepository,
    PlayerRepository,
    SelectedGameRoleRepository,
    TeamPlayerRepository,
    TeamRepository,
)
from ._base import BaseService

logger = logging.getLogger(__name__)


class TeamService(BaseService):
    """Manages teams after formation — roster, naming, captaincy, premade registration."""

    def __init__(
        self,
        team_repo: TeamRepository,
        team_player_repo: TeamPlayerRepository,
        event_repo: EventRepository,
        organizer_repo: OrganizerRepository,
        player_repo: PlayerRepository,
        game_role_repo: SelectedGameRoleRepository,
        drafted_player_repo: DraftedPlayerRepository,
    ) -> None:
        self._team_repo = team_repo
        self._tp_repo = team_player_repo
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._player_repo = player_repo
        self._game_role_repo = game_role_repo
        self._dp_repo = drafted_player_repo

    # ── private helpers ──────────────────────────

    async def _assert_organizer_or_captain(
        self,
        event_id: UUID,
        team_id: UUID,
        member_id: UUID,
    ) -> None:
        """Allow if caller is an event organizer **or** the team's draft captain."""
        organizers = await self._organizer_repo.list_by_event(event_id)
        if any(o.member_id == member_id for o in organizers):
            return

        team = await self._team_repo.get(team_id)
        if team is not None and team.draft_id is not None:
            player = await self._player_repo.get_by_event_and_member(event_id, member_id)
            if player is not None:
                drafted = await self._dp_repo.list_by_draft(team.draft_id)
                if any(dp.event_player_id == player.id and dp.is_captain for dp in drafted):
                    return

        raise ForbiddenException("Only an organizer or team captain can perform this action")

    async def _get_team_or_404(self, team_id: UUID, *, load_players: bool = False) -> Team:
        """Fetch a team by id or raise ``NotFoundException``."""
        team = await self._team_repo.get(team_id, load_players=load_players)
        if team is None:
            raise NotFoundException("Team not found")
        return team

    async def _collect_taken_member_ids(self, event_id: UUID) -> set[UUID]:
        """Return the set of ``member_id`` values already assigned to any team in the event."""
        taken: set[UUID] = set()
        for t in await self._team_repo.list_by_event(event_id):
            for tp in await self._tp_repo.list_by_team(t.id):
                taken.add(tp.member_id)
        return taken

    # ── premade registration ─────────────────────

    async def register_premade_team(
        self,
        event_id: UUID,
        captain_id: UUID,
        player_member_ids: list[UUID],
        name: str,
        *,
        game_role_id: UUID | None = None,
    ) -> Team:
        """
        Register a pre-formed team for a tournament.

        *captain_id* must be among *player_member_ids*.
        All members must already be registered ``EventPlayer`` rows.
        """
        event = await self._fetch_event(event_id)

        if captain_id not in player_member_ids:
            raise BadRequestException("Captain must be one of the team players")
        if len(player_member_ids) != event.team_size:
            raise BadRequestException(f"Team must have exactly {event.team_size} players")

        # all members must be EventPlayers
        registered = {p.member_id for p in await self._player_repo.list_by_event(event_id)}
        missing = set(player_member_ids) - registered
        if missing:
            raise BadRequestException(f"Members not registered for the event: {missing}")

        # no member may already sit on another team
        taken = await self._collect_taken_member_ids(event_id)
        overlap = set(player_member_ids) & taken
        if overlap:
            raise ConflictException(f"Members already on a team: {overlap}")

        # resolve default game role when none supplied
        if game_role_id is None:
            roles = await self._game_role_repo.list_by_event(event_id)
            if not roles:
                raise BadRequestException("Event has no game roles configured")
            game_role_id = roles[0].id

        team = await self._team_repo.create(Team(event_id=event_id, name=name, draft_id=None))

        for mid in player_member_ids:
            await self._tp_repo.create(
                TeamPlayer(team_id=team.id, member_id=mid, game_role_id=game_role_id, rating=0.0),
            )

        logger.info(
            "Premade team '%s' registered for event %s (%d players)",
            name, event_id, len(player_member_ids),
        )
        return team

    # ── rename ───────────────────────────────────

    async def rename_team(self, team_id: UUID, requester_id: UUID, new_name: str) -> Team:
        """Rename a team. Organizer or captain only."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        stripped = new_name.strip()
        if not stripped:
            raise BadRequestException("Team name cannot be empty")

        team.name = stripped
        team = await self._team_repo.update(team)
        logger.info("Team %s renamed to '%s'", team_id, team.name)
        return team

    # ── captaincy ────────────────────────────────

    async def appoint_captain(
        self,
        team_id: UUID,
        requester_id: UUID,
        member_id: UUID,
    ) -> None:
        """
        Appoint *member_id* as captain of the team.

        The previous captain (if any) is demoted.  Only works for
        draft-originated teams that track captaincy via ``DraftedPlayer``.
        Organizer or current captain only.
        """
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        if team.draft_id is None:
            raise BadRequestException("Captaincy is only tracked for draft-originated teams")

        # verify the target is actually on the roster
        roster = await self._tp_repo.list_by_team(team_id)
        if not any(tp.member_id == member_id for tp in roster):
            raise NotFoundException("Player not found on this team")

        # resolve the target's EventPlayer
        target_player = await self._player_repo.get_by_event_and_member(team.event_id, member_id)
        if target_player is None:
            raise NotFoundException("Player is not registered for this event")

        drafted = await self._dp_repo.list_by_draft(team.draft_id)

        # demote existing captain(s) and promote the target
        for dp in drafted:
            if dp.is_captain:
                dp.is_captain = False
                await self._dp_repo.update(dp)
            if dp.event_player_id == target_player.id:
                dp.is_captain = True
                await self._dp_repo.update(dp)

        logger.info("Team %s: appointed %s as captain", team_id, member_id)

    # ── roster management ────────────────────────

    async def add_player(
        self,
        team_id: UUID,
        requester_id: UUID,
        member_id: UUID,
        game_role_id: UUID,
        *,
        rating: float = 0.0,
    ) -> TeamPlayer:
        """Add a player to the roster. Validates ``team_size`` cap."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        event = await self._fetch_event(team.event_id)
        roster = await self._tp_repo.list_by_team(team_id)
        if len(roster) >= event.team_size:
            raise ConflictException("Team is already full")

        try:
            tp = await self._tp_repo.create(
                TeamPlayer(team_id=team_id, member_id=member_id, game_role_id=game_role_id, rating=rating),
            )
        except IntegrityUniqueException:
            raise ConflictException("Player is already on this team")

        logger.info("Added member %s to team %s", member_id, team_id)
        return tp

    async def remove_player(self, team_id: UUID, requester_id: UUID, member_id: UUID) -> None:
        """Remove a player from the roster. Organizer or captain only."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        roster = await self._tp_repo.list_by_team(team_id)
        tp = next((t for t in roster if t.member_id == member_id), None)
        if tp is None:
            raise NotFoundException("Player not found on this team")

        await self._tp_repo.delete(tp.id)
        logger.info("Removed member %s from team %s", member_id, team_id)

    async def substitute_player(
        self,
        team_id: UUID,
        requester_id: UUID,
        old_member_id: UUID,
        new_member_id: UUID,
    ) -> TeamPlayer:
        """
        Replace one player with another — keeps the game role and rating.

        The incoming player must not already belong to another team
        in the same event.
        """
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        roster = await self._tp_repo.list_by_team(team_id)
        old_tp = next((t for t in roster if t.member_id == old_member_id), None)
        if old_tp is None:
            raise NotFoundException("Original player not found on this team")

        # ensure the incoming player isn't on another team in this event
        taken = await self._collect_taken_member_ids(team.event_id)
        own_members = {t.member_id for t in roster}
        if new_member_id in (taken - own_members):
            raise ConflictException(f"Member {new_member_id} is already on another team in this event")

        saved_role = old_tp.game_role_id
        saved_rating = old_tp.rating
        await self._tp_repo.delete(old_tp.id)

        try:
            new_tp = await self._tp_repo.create(
                TeamPlayer(
                    team_id=team_id,
                    member_id=new_member_id,
                    game_role_id=saved_role,
                    rating=saved_rating,
                ),
            )
        except IntegrityUniqueException:
            raise ConflictException("New member is already on this team")

        logger.info("Team %s: substituted %s → %s", team_id, old_member_id, new_member_id)
        return new_tp

    async def set_player_role(
        self,
        team_id: UUID,
        requester_id: UUID,
        member_id: UUID,
        game_role_id: UUID,
    ) -> TeamPlayer:
        """Change a player's game role. Organizer or captain only."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer_or_captain(team.event_id, team_id, requester_id)

        roster = await self._tp_repo.list_by_team(team_id)
        tp = next((t for t in roster if t.member_id == member_id), None)
        if tp is None:
            raise NotFoundException("Player not found on this team")

        tp.game_role_id = game_role_id
        return await self._tp_repo.update(tp)

    async def set_player_rating(
        self,
        team_id: UUID,
        requester_id: UUID,
        member_id: UUID,
        rating: float,
    ) -> TeamPlayer:
        """Manually override a player's rating. Organizer only."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer(team.event_id, requester_id)

        roster = await self._tp_repo.list_by_team(team_id)
        tp = next((t for t in roster if t.member_id == member_id), None)
        if tp is None:
            raise NotFoundException("Player not found on this team")

        tp.rating = rating
        return await self._tp_repo.update(tp)

    # ── read helpers ─────────────────────────────

    async def get_team(self, team_id: UUID) -> Team:
        """Return a single team with its roster loaded."""
        return await self._get_team_or_404(team_id, load_players=True)

    async def list_teams(self, event_id: UUID) -> Sequence[Team]:
        """List all teams for an event (lightweight — no players eager-loaded)."""
        await self._fetch_event(event_id)
        return await self._team_repo.list_by_event(event_id)

    async def get_roster(self, team_id: UUID) -> Sequence[TeamPlayer]:
        """Return every ``TeamPlayer`` row for the team."""
        await self._get_team_or_404(team_id)
        return await self._tp_repo.list_by_team(team_id)

    async def get_team_average_rating(self, team_id: UUID) -> float:
        """Compute the arithmetic mean of player ratings on the team."""
        roster = await self._tp_repo.list_by_team(team_id)
        if not roster:
            return 0.0
        return sum(tp.rating for tp in roster) / len(roster)

    # ── deletion ─────────────────────────────────

    async def disband_team(self, team_id: UUID, requester_id: UUID) -> None:
        """Hard-delete team and all roster rows (cascade). Organizer only."""
        team = await self._get_team_or_404(team_id)
        await self._assert_organizer(team.event_id, requester_id)
        await self._team_repo.delete(team_id)
        logger.info("Team %s disbanded by %s", team_id, requester_id)

