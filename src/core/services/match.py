from datetime import datetime, timezone
from uuid import UUID

from src.core.commands.match import GetMatchCommand, ListMatchesCommand, RecordMatchResultCommand, SetupMatchCommand
from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from src.core.interfaces.repo.bracket import BracketRepositoryProtocol
from src.core.interfaces.repo.draft import DraftRepositoryProtocol
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.match import MatchRepositoryProtocol
from src.core.interfaces.repo.match_score import MatchScoreRepositoryProtocol
from src.core.interfaces.repo.match_slot import MatchSlotRepositoryProtocol
from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.interfaces.repo.stage import StageRepositoryProtocol
from src.core.interfaces.repo.stage_group import StageGroupRepositoryProtocol
from src.core.interfaces.repo.team import TeamRepositoryProtocol
from src.core.models.bracket import Bracket, BracketCreate
from src.core.models.event import EventMatchType, EventStatus
from src.core.models.event_player import EventPlayerStatus, EventPlayerUpdate
from src.core.models.match import Match, MatchCreate, MatchUpdate
from src.core.models.match_score import MatchScoreCreate, MatchScoreUpdate
from src.core.models.match_slot import MatchSlotCreate, MatchSlotSourceType
from src.core.models.stage import Stage, StageCreate, StageFormat
from src.core.models.stage_group import StageGroup, StageGroupCreate
from src.core.models.team import Team
from src.core.results.match import RecordedMatchResult, SingleMatchSlotView, SingleMatchView
from src.core.interfaces.repo.access import (
    P_EVENT_ADMIN_COMPLETE,
    P_EVENT_ADMIN_MANAGE_BRACKET,
    P_EVENT_ADMIN_VIEW,
    has_event_admin_permission,
    is_same_server,
)


class MatchService:
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        bracket_repo: BracketRepositoryProtocol,
        stage_repo: StageRepositoryProtocol,
        stage_group_repo: StageGroupRepositoryProtocol,
        match_repo: MatchRepositoryProtocol,
        match_slot_repo: MatchSlotRepositoryProtocol,
        match_score_repo: MatchScoreRepositoryProtocol,
        team_repo: TeamRepositoryProtocol,
        draft_repo: DraftRepositoryProtocol,
        player_repo: PlayerRepositoryProtocol,
        rating_client,
        env,
    ):
        self._event_repo = event_repo
        self._bracket_repo = bracket_repo
        self._stage_repo = stage_repo
        self._stage_group_repo = stage_group_repo
        self._match_repo = match_repo
        self._match_slot_repo = match_slot_repo
        self._match_score_repo = match_score_repo
        self._team_repo = team_repo
        self._draft_repo = draft_repo
        self._player_repo = player_repo
        self._rating_client = rating_client
        self._env = env

    async def setup(self, cmd: SetupMatchCommand) -> SingleMatchView:
        event = await self._event_repo.get(
            cmd.event_id,
            load_organizers=True,
            load_integrations=False,
            load_time_settings=False,
            load_game_roles=False,
            load_custom_fields=False,
            load_applications=False,
            load_teams=False,
            load_drafts=False,
            load_players=False,
            load_brackets=False,
        )
        if event is None:
            raise NotFoundException(f"Event {cmd.event_id} not found")

        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")

        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(
            cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET
        ) or has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_COMPLETE)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can setup matches")

        if event.match_type != EventMatchType.SINGLE:
            raise BadRequestException("Single match setup is only available for single-game events")
        if event.status in (EventStatus.CREATED, EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise ConflictException(f"Event status {event.status.value} does not allow match setup")
        if len(cmd.team_ids) < 2:
            raise BadRequestException("At least two teams are required for single match setup")
        if len(set(cmd.team_ids)) != len(cmd.team_ids):
            raise BadRequestException("Duplicate team ids are not allowed")

        teams = await self._load_teams(cmd.team_ids, cmd.event_id)
        draft_id = await self._resolve_draft_id(cmd.draft_id, teams, cmd.event_id)
        await self._validate_not_busy(cmd.event_id, cmd.team_ids, draft_id, event.allow_multiple_drafts)

        bracket = await self._get_or_create_bracket(cmd.event_id)
        stage = await self._get_or_create_stage(bracket.id)
        group = await self._get_or_create_group(stage.id)

        match_index = await self._match_repo.next_match_index(group.id)
        match = await self._match_repo.create(MatchCreate(
            group_id=group.id,
            match_index=match_index,
            scheduled_at=cmd.scheduled_at,
            round_number=match_index,
        ))

        slots: list[SingleMatchSlotView] = []
        for slot_num, team_id in enumerate(cmd.team_ids, start=1):
            slot = await self._match_slot_repo.create(MatchSlotCreate(
                match_id=match.id,
                slot_num=slot_num,
                source_type=MatchSlotSourceType.MANUAL,
            ))
            score = await self._match_score_repo.create(MatchScoreCreate(
                slot_id=slot.id,
                team_id=team_id,
                score=0,
            ))
            slots.append(SingleMatchSlotView(
                slot_id=slot.id,
                slot_num=slot.slot_num,
                team_id=team_id,
                score_id=score.id,
                score=score.score,
            ))

        return SingleMatchView(
            event_id=cmd.event_id,
            bracket_id=bracket.id,
            stage_id=stage.id,
            group_id=group.id,
            match_id=match.id,
            match_index=match_index,
            draft_id=draft_id,
            slots=slots,
        )

    async def record_result(self, cmd: RecordMatchResultCommand) -> RecordedMatchResult:
        context = await self._match_repo.get_event_context(cmd.match_id)
        if context is None:
            raise NotFoundException(f"Match {cmd.match_id} not found")
        event_id, server_id, stage_format, bracket_id, stage_id, group_id = context

        event = await self._event_repo.get(
            event_id,
            load_organizers=True,
            load_integrations=False,
            load_time_settings=False,
            load_game_roles=False,
            load_custom_fields=False,
            load_applications=False,
            load_teams=False,
            load_drafts=False,
            load_players=False,
            load_brackets=False,
        )
        if event is None:
            raise NotFoundException(f"Event {event_id} not found")
        if server_id != event.server_id or not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Match belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can record match results")
        if event.match_type != EventMatchType.SINGLE or stage_format != StageFormat.SINGLE_MATCH:
            raise BadRequestException("Only single-game matches can be completed at this stage")

        match = await self._match_repo.get(cmd.match_id, load_slots=True, load_group=False)
        if match is None:
            raise NotFoundException(f"Match {cmd.match_id} not found")
        if match.time_end is not None:
            raise ConflictException("Match result is already recorded")
        if not match.slots:
            raise BadRequestException("Match has no slots")

        team_ids = self._validate_scores(match, cmd.scores)
        forfeit_team_ids = set(cmd.forfeit_team_ids)
        unknown_forfeits = forfeit_team_ids.difference(team_ids)
        if unknown_forfeits:
            raise BadRequestException(f"Unknown forfeit team ids: {sorted(str(t) for t in unknown_forfeits)}")

        ranks_by_team, winner_team_id, loser_team_ids, is_draw = self._resolve_result(
            team_ids,
            cmd.scores,
            cmd.winner_id,
            cmd.is_draw,
            forfeit_team_ids,
        )

        now = datetime.now(timezone.utc)
        rating_payload = await self._build_rating_payload(event_id, cmd.match_id, now, team_ids, ranks_by_team, cmd.rating_settings)
        ordered_forfeit_team_ids = [team_id for team_id in team_ids if team_id in forfeit_team_ids]
        snapshot = {
            "match_id": str(cmd.match_id),
            "event_id": str(event_id),
            "scores": {str(team_id): cmd.scores[team_id] for team_id in team_ids},
            "winner_team_id": str(winner_team_id) if winner_team_id else None,
            "loser_team_ids": [str(team_id) for team_id in loser_team_ids],
            "is_draw": is_draw,
            "forfeit_team_ids": [str(team_id) for team_id in ordered_forfeit_team_ids],
            "rating_payload": rating_payload,
            "rating_published": False,
            "completed_at": now.isoformat(),
        }

        for slot in match.slots:
            if slot.score is None:
                raise BadRequestException(f"Slot {slot.id} has no score row")
            await self._match_score_repo.update(slot.score.id, MatchScoreUpdate(score=cmd.scores[slot.score.team_id]))

        for team_id in team_ids:
            team = await self._team_repo.get(team_id, load_event=False, load_players=True)
            if team is None:
                raise NotFoundException(f"Team {team_id} not found")
            for team_player in team.players:
                player = await self._player_repo.get_by_event_and_member(event_id, team_player.member_id)
                if player is not None:
                    await self._player_repo.update(player.id, EventPlayerUpdate(status=EventPlayerStatus.REGISTERED))

        rating_published = False
        if self._env.rating_match_process_enabled:
            await self._rating_client.process_match_result(**rating_payload)
            rating_published = True
            snapshot["rating_published"] = True

        updated = await self._match_repo.update(
            cmd.match_id,
            MatchUpdate(
                time_start=match.time_start or now,
                time_end=now,
                result_snapshot=snapshot,
            ),
        )
        updated_view = await _build_single_match_view(
            updated,
            event_id,
            bracket_id,
            stage_id,
            group_id,
            self._team_repo,
        )
        return RecordedMatchResult(
            match=updated_view,
            winner_team_id=winner_team_id,
            loser_team_ids=loser_team_ids,
            is_draw=is_draw,
            forfeit_team_ids=ordered_forfeit_team_ids,
            team_ranks=[ranks_by_team[team_id] for team_id in team_ids],
            rating_payload=rating_payload,
            rating_published=rating_published,
        )

    async def get(self, cmd: GetMatchCommand) -> SingleMatchView:
        context = await self._match_repo.get_event_context(cmd.match_id)
        if context is None:
            raise NotFoundException(f"Match {cmd.match_id} not found")
        event_id, server_id, _stage_format, bracket_id, stage_id, group_id = context
        event = await self._event_repo.get(event_id, load_organizers=True)
        if event is None:
            raise NotFoundException(f"Event {event_id} not found")
        if server_id != event.server_id:
            raise NotFoundException(f"Match {cmd.match_id} not found")
        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Match belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_VIEW) or has_event_admin_permission(
            cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET
        )
        if not event.is_public and not is_organizer and not is_admin:
            raise ForbiddenException("Access denied")

        match = await self._match_repo.get(cmd.match_id, load_slots=True, load_group=False)
        if match is None:
            raise NotFoundException(f"Match {cmd.match_id} not found")
        return await _build_single_match_view(match, event_id, bracket_id, stage_id, group_id, self._team_repo)

    async def get_list(self, cmd: ListMatchesCommand) -> list[SingleMatchView]:
        event = await self._event_repo.get(cmd.event_id, load_organizers=True)
        if event is None:
            raise NotFoundException(f"Event {cmd.event_id} not found")
        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_VIEW) or has_event_admin_permission(
            cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET
        )
        if not event.is_public and not is_organizer and not is_admin:
            raise ForbiddenException("Access denied")

        offset = (cmd.pagination.page - 1) * cmd.pagination.page_size if cmd.pagination.page else 0
        matches = await self._match_repo.list_by_event(cmd.event_id, offset, cmd.pagination.page_size, active=cmd.active)
        result = []
        for match in matches:
            context = await self._match_repo.get_event_context(match.id)
            if context is None:
                continue
            event_id, _server_id, _stage_format, bracket_id, stage_id, group_id = context
            result.append(await _build_single_match_view(match, event_id, bracket_id, stage_id, group_id, self._team_repo))
        return result

    async def _load_teams(self, team_ids: list[UUID], event_id: UUID) -> list[Team]:
        teams: list[Team] = []
        for team_id in team_ids:
            team = await self._team_repo.get(team_id, load_event=False, load_players=True)
            if team is None:
                raise NotFoundException(f"Team {team_id} not found")
            if team.event_id != event_id:
                raise BadRequestException(f"Team {team_id} belongs to a different event")
            if not team.players:
                raise BadRequestException(f"Team {team_id} has no players")
            teams.append(team)
        return teams

    async def _resolve_draft_id(self, command_draft_id: UUID | None, teams: list[Team], event_id: UUID) -> UUID | None:
        team_draft_ids = {team.draft_id for team in teams if team.draft_id is not None}
        if command_draft_id is not None:
            draft = await self._draft_repo.get(command_draft_id, load_drafted_players=False)
            if draft is None:
                raise NotFoundException(f"Draft {command_draft_id} not found")
            if draft.event_id != event_id:
                raise BadRequestException("Draft belongs to a different event")
            if any(team.draft_id is not None and team.draft_id != command_draft_id for team in teams):
                raise BadRequestException("Team draft_id does not match command draft_id")
            return command_draft_id
        if len(team_draft_ids) > 1:
            raise BadRequestException("Teams from different drafts cannot be mixed in one match")
        return next(iter(team_draft_ids), None)

    async def _validate_not_busy(
        self,
        event_id: UUID,
        team_ids: list[UUID],
        draft_id: UUID | None,
        allow_multiple_drafts: bool,
    ) -> None:
        active_team_ids = await self._match_repo.list_active_team_ids_by_event(event_id)
        busy_team_ids = active_team_ids.intersection(team_ids)
        if busy_team_ids:
            raise ConflictException(f"Teams are already assigned to an active match: {sorted(str(t) for t in busy_team_ids)}")

        if draft_id is None:
            return
        active_draft_ids = await self._match_repo.list_active_draft_ids_by_event(event_id)
        if draft_id in active_draft_ids:
            raise ConflictException(f"Draft {draft_id} is already linked to an active match")
        if not allow_multiple_drafts and active_draft_ids:
            raise ConflictException("Event already has active match draft and parallel drafts are disabled")

    async def _get_or_create_bracket(self, event_id: UUID) -> Bracket:
        brackets = await self._bracket_repo.list_by_event(event_id, 0, 1)
        if brackets:
            return brackets[0]
        return await self._bracket_repo.create(BracketCreate(event_id=event_id))

    async def _get_or_create_stage(self, bracket_id: UUID) -> Stage:
        stages = await self._stage_repo.list_by_bracket(bracket_id, 0, 100)
        for stage in stages:
            if stage.format == StageFormat.SINGLE_MATCH:
                return stage
        if stages:
            raise ConflictException("Bracket already contains non-single-match stages")
        return await self._stage_repo.create(StageCreate(
            bracket_id=bracket_id,
            stage_index=0,
            format=StageFormat.SINGLE_MATCH,
            name="Single Matches",
        ))

    async def _get_or_create_group(self, stage_id: UUID) -> StageGroup:
        groups = await self._stage_group_repo.list_by_stage(stage_id)
        if groups:
            return groups[0]
        return await self._stage_group_repo.create(StageGroupCreate(
            stage_id=stage_id,
            name="Single Match Group",
            advance_count=None,
        ))

    def _validate_scores(self, match: Match, scores: dict[UUID, int]) -> list[UUID]:
        team_ids: list[UUID] = []
        for slot in sorted(match.slots, key=lambda item: item.slot_num):
            if slot.score is None:
                raise BadRequestException(f"Slot {slot.id} has no score row")
            team_ids.append(slot.score.team_id)
        if len(team_ids) < 2:
            raise BadRequestException("At least two filled slots are required")
        missing = set(team_ids).difference(scores)
        extra = set(scores).difference(team_ids)
        if missing:
            raise BadRequestException(f"Missing scores for teams: {sorted(str(t) for t in missing)}")
        if extra:
            raise BadRequestException(f"Scores contain unknown teams: {sorted(str(t) for t in extra)}")
        if any(score < 0 for score in scores.values()):
            raise BadRequestException("Scores cannot be negative")
        return team_ids

    def _resolve_result(
        self,
        team_ids: list[UUID],
        scores: dict[UUID, int],
        winner_id: UUID | None,
        is_draw_requested: bool,
        forfeit_team_ids: set[UUID],
    ) -> tuple[dict[UUID, float], UUID | None, list[UUID], bool]:
        if forfeit_team_ids:
            if winner_id is not None or is_draw_requested:
                raise BadRequestException("Forfeit result cannot also declare winner_id or draw")
            if forfeit_team_ids == set(team_ids):
                raise BadRequestException("All teams cannot forfeit one match")
            winner_candidates = [team_id for team_id in team_ids if team_id not in forfeit_team_ids]
            winner_team_id = winner_candidates[0] if len(winner_candidates) == 1 else None
            ranks = {team_id: (2.0 if team_id in forfeit_team_ids else 1.0) for team_id in team_ids}
            return ranks, winner_team_id, list(forfeit_team_ids), False

        if winner_id is not None:
            if is_draw_requested:
                raise BadRequestException("Draw result cannot also declare winner_id")
            if winner_id not in team_ids:
                raise BadRequestException("winner_id does not belong to match teams")
            ranks = {team_id: (1.0 if team_id == winner_id else 2.0) for team_id in team_ids}
            return ranks, winner_id, [team_id for team_id in team_ids if team_id != winner_id], False

        if is_draw_requested:
            return {team_id: 1.0 for team_id in team_ids}, None, [], True

        max_score = max(scores[team_id] for team_id in team_ids)
        winners = [team_id for team_id in team_ids if scores[team_id] == max_score]
        is_draw = len(winners) > 1
        if is_draw:
            ranks = {team_id: (1.0 if team_id in winners else 2.0) for team_id in team_ids}
            return ranks, None, [], True

        winner_team_id = winners[0]
        ranks = {team_id: (1.0 if team_id == winner_team_id else 2.0) for team_id in team_ids}
        return ranks, winner_team_id, [team_id for team_id in team_ids if team_id != winner_team_id], False

    async def _build_rating_payload(
        self,
        event_id: UUID,
        match_id: UUID,
        match_time: datetime,
        team_ids: list[UUID],
        ranks_by_team: dict[UUID, float],
        rating_settings: dict[str, str | int | float | bool | None] | None,
    ) -> dict:
        teams_payload = []
        players_payload = []
        for team_id in team_ids:
            team = await self._team_repo.get(team_id, load_event=False, load_players=True)
            if team is None:
                raise NotFoundException(f"Team {team_id} not found")
            if team.event_id != event_id:
                raise BadRequestException(f"Team {team_id} belongs to a different event")
            member_ids = [player.member_id for player in team.players]
            teams_payload.append({
                "team_id": str(team_id),
                "player_ids": [str(member_id) for member_id in member_ids],
            })
            for player in team.players:
                players_payload.append({
                    "member_id": str(player.member_id),
                    "role_id": str(player.game_role_id),
                    "open_rating": float(player.rating),
                })

        rating_settings = rating_settings or {}
        return {
            "match_id": str(match_id),
            "match_time": match_time.isoformat(),
            "teams": teams_payload,
            "team_ranks": [ranks_by_team[team_id] for team_id in team_ids],
            "players": players_payload,
            "settings": rating_settings,
        }


async def _build_single_match_view(
    match: Match,
    event_id: UUID,
    bracket_id: UUID,
    stage_id: UUID,
    group_id: UUID,
    team_repo: TeamRepositoryProtocol,
) -> SingleMatchView:
    slots: list[SingleMatchSlotView] = []
    draft_ids: set[UUID] = set()
    for slot in sorted(match.slots, key=lambda item: item.slot_num):
        if slot.score is None:
            continue
        team = await team_repo.get(slot.score.team_id, load_event=False, load_players=False)
        if team is not None and team.draft_id is not None:
            draft_ids.add(team.draft_id)
        slots.append(SingleMatchSlotView(
            slot_id=slot.id,
            slot_num=slot.slot_num,
            team_id=slot.score.team_id,
            score_id=slot.score.id,
            score=slot.score.score,
        ))
    draft_id = next(iter(draft_ids), None) if len(draft_ids) <= 1 else None
    return SingleMatchView(
        event_id=event_id,
        bracket_id=bracket_id,
        stage_id=stage_id,
        group_id=group_id,
        match_id=match.id,
        match_index=match.match_index or 0,
        draft_id=draft_id,
        completed_at=match.time_end,
        result_snapshot=match.result_snapshot,
        slots=slots,
    )
