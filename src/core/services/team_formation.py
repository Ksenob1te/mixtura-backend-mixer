import uuid
from uuid import UUID

from src.core.commands.team_formation import (
    RunTeamFormationCommand,
    GetTeamFormationCommand,
    ChooseTeamFormationVariantCommand,
)
from src.core.exceptions import NotFoundException, ForbiddenException, ConflictException, BadRequestException
from src.core.interfaces.repo.draft import DraftRepositoryProtocol
from src.core.interfaces.repo.event import EventRepositoryProtocol
from src.core.interfaces.repo.organizer import OrganizerRepositoryProtocol
from src.core.interfaces.repo.player import PlayerRepositoryProtocol
from src.core.interfaces.repo.team import TeamRepositoryProtocol
from src.core.interfaces.repo.team_player import TeamPlayerRepositoryProtocol
from src.core.interfaces.repo.balancer_request import BalancerRequestRepositoryProtocol
from src.core.interfaces.repo.balancer_task import BalancerTaskStoreProtocol
from src.core.interfaces.repo.rating import RatingClientProtocol
from src.core.interfaces.repo.team_formation_variant import TeamFormationVariantStoreProtocol
from src.core.models.balancer import (
    BalancerPlayer,
    BalancerPlayerRole,
    BalancerTeam,
    MixBalanceSettings,
    MixBalancerResult,
    MixRoleConfig,
    TournamentBalanceSettings,
    TournamentBalancerResult,
    TournamentRoleConfig,
)
from src.core.models.rating import RatingPlayerRequest, RatingSettings
from src.core.models.draft import DraftStatus, DraftUpdate
from src.core.models.event_player import EventPlayerStatus, EventPlayerUpdate
from src.core.models.event import EventMatchType, TeamFormation as TeamFormationMethod
from src.core.models.team import TeamCreate
from src.core.models.team_player import TeamPlayerCreate
from src.core.results.balancer_task import BalancerTask, RatingSnapshotPlayerFull
from src.core.results.team import TeamDetail
from src.core.results.team_formation import (
    TeamFormationJob,
    TeamFormationVariant,
    TeamFormationVariantTeam,
    RatingSnapshotPlayer,
)
from src.core.interfaces.repo.access import (
    P_EVENT_ADMIN_MANAGE_BRACKET,
    has_event_admin_permission,
    is_same_server,
)


def _get_first_role(event):
    roles = event.selected_game_roles
    if roles:
        return roles[0].id
    return uuid.uuid4()


class TeamFormationService:
    def __init__(
        self,
        event_repo: EventRepositoryProtocol,
        organizer_repo: OrganizerRepositoryProtocol,
        draft_repo: DraftRepositoryProtocol,
        player_repo: PlayerRepositoryProtocol,
        team_repo: TeamRepositoryProtocol,
        team_player_repo: TeamPlayerRepositoryProtocol,
        variant_store: TeamFormationVariantStoreProtocol,
        rating_client: RatingClientProtocol,
        balancer_repo: BalancerRequestRepositoryProtocol,
        balancer_task_store: BalancerTaskStoreProtocol,
        env,
    ):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._draft_repo = draft_repo
        self._player_repo = player_repo
        self._team_repo = team_repo
        self._team_player_repo = team_player_repo
        self._variant_store = variant_store
        self._rating_client = rating_client
        self._balancer_repo = balancer_repo
        self._balancer_task_store = balancer_task_store
        self._env = env

    async def run(self, cmd: RunTeamFormationCommand) -> TeamFormationJob:
        draft = await self._draft_repo.get(cmd.draft_id, load_drafted_players=True)
        if draft is None:
            raise NotFoundException(f"Draft {cmd.draft_id} not found")

        event = await self._event_repo.get(
            draft.event_id,
            load_organizers=True,
            load_game_roles=True,
            load_integrations=False,
            load_time_settings=False,
            load_custom_fields=False,
            load_applications=False,
            load_teams=False,
            load_drafts=False,
            load_players=False,
            load_brackets=False,
        )
        if event is None:
            raise NotFoundException(f"Event {draft.event_id} not found")

        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can run team formation")

        if draft.status not in (DraftStatus.OPEN, DraftStatus.BALANCE_REQUESTED):
            raise ConflictException(f"Cannot run team formation for draft status {draft.status.value}")

        if draft.status == DraftStatus.BALANCE_REQUESTED:
            job = await self._variant_store.get_latest_by_draft(draft.event_id, cmd.draft_id)
            if job is not None and job.status == "pending":
                raise ConflictException(
                    "Team formation is still in progress. Wait for completion before re-running."
                )

        if event.team_formation != TeamFormationMethod.BALANCE:
            raise BadRequestException(f"Event team formation method is {event.team_formation.value}, not BALANCE")

        rating_snapshot = await self._build_rating_snapshot(draft, event, cmd)

        task_id = uuid.uuid4()

        players_with_roles = []
        for dp in draft.drafted_players:
            player = await self._player_repo.get(dp.event_player_id, load_roles=True, load_drafted=False)
            if player:
                players_with_roles.append(player)

        balancer_players = self._build_balancer_players(players_with_roles, rating_snapshot)
        event_player_by_member = {player.member_id: player.id for player in players_with_roles}
        role_by_member = {item.member_id: item.game_role_id for item in rating_snapshot}

        ttl = self._env.team_formation_variants_ttl_seconds
        task = BalancerTask(
            task_id=task_id,
            draft_id=cmd.draft_id,
            event_id=draft.event_id,
            status="pending",
            event_player_by_member=event_player_by_member,
            role_by_member=role_by_member,
            rating_snapshot=rating_snapshot,
        )
        await self._balancer_task_store.save(task, ttl)

        pending_job = TeamFormationJob(
            job_id=task_id,
            draft_id=cmd.draft_id,
            event_id=draft.event_id,
            status="pending",
            variants=[],
            rating_snapshot=[RatingSnapshotPlayer(**s.model_dump()) for s in rating_snapshot],
        )
        await self._variant_store.save(task_id, draft.event_id, cmd.draft_id, pending_job, ttl)

        if event.match_type == EventMatchType.TOURNAMENT:
            settings, normalized_players = self._build_tournament_balancer_request(
                event, balancer_players, cmd
            )
            await self._balancer_repo.request_tournament_formation(
                task_id=task_id,
                draft_id=cmd.draft_id,
                players=normalized_players,
                settings=settings,
            )
        else:
            settings, normalized_players = self._build_mix_balancer_request(
                event, balancer_players, cmd
            )
            await self._balancer_repo.request_mix_formation(
                task_id=task_id,
                draft_id=cmd.draft_id,
                players=normalized_players,
                settings=settings,
            )

        await self._draft_repo.update(DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_REQUESTED))

        return pending_job

    async def complete_formation(
        self, task_id: UUID, result: MixBalancerResult | TournamentBalancerResult
    ) -> None:
        task = await self._balancer_task_store.get(task_id)
        if task is None:
            return

        event_player_by_member = task.event_player_by_member
        role_by_member = task.role_by_member

        variants: list[TeamFormationVariant] = []
        for i, balance in enumerate(result.balances):
            variant_id = uuid.uuid4()
            quality = balance.quality
            variant_teams = []
            for ti, bt in enumerate(balance.teams):
                member_ids, event_player_ids, game_role_ids, calculated_ratings = self._extract_team_players(
                    bt, event_player_by_member, role_by_member,
                )
                variant_teams.append(TeamFormationVariantTeam(
                    team_index=ti,
                    name=f"Team {ti + 1}",
                    member_ids=member_ids,
                    event_player_ids=event_player_ids,
                    game_role_ids=game_role_ids,
                    calculated_ratings=calculated_ratings,
                ))
            variants.append(TeamFormationVariant(
                id=variant_id,
                draft_id=task.draft_id,
                teams=variant_teams,
                metrics=quality,
            ))

        job = TeamFormationJob(
            job_id=task_id,
            draft_id=task.draft_id,
            event_id=task.event_id,
            status="completed",
            variants=variants,
            rating_snapshot=[RatingSnapshotPlayer(**s.model_dump()) for s in task.rating_snapshot],
        )

        ttl = self._env.team_formation_variants_ttl_seconds
        await self._variant_store.save(task_id, task.event_id, task.draft_id, job, ttl)
        await self._balancer_task_store.delete(task_id)

    async def get(self, cmd: GetTeamFormationCommand) -> TeamFormationJob:
        draft = await self._draft_repo.get(cmd.draft_id, load_drafted_players=False)
        if draft is None:
            raise NotFoundException(f"Draft {cmd.draft_id} not found")

        event = await self._event_repo.get(
            draft.event_id,
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
            raise NotFoundException(f"Event {draft.event_id} not found")
        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Access denied")

        job = await self._variant_store.get_latest_by_draft(draft.event_id, cmd.draft_id)
        if job is None:
            raise NotFoundException("Team formation job not found or expired, run team formation again")

        offset = (cmd.pagination.page - 1) * cmd.pagination.page_size if cmd.pagination.page else 0
        limit = cmd.pagination.page_size
        return job.model_copy(update={"variants": job.variants[offset:offset + limit]})

    async def choose_variant(self, cmd: ChooseTeamFormationVariantCommand) -> list[TeamDetail]:
        draft = await self._draft_repo.get(cmd.draft_id, load_drafted_players=True)
        if draft is None:
            raise NotFoundException(f"Draft {cmd.draft_id} not found")

        event = await self._event_repo.get(
            draft.event_id,
            load_organizers=True,
            load_game_roles=True,
            load_integrations=False,
            load_time_settings=False,
            load_custom_fields=False,
            load_applications=False,
            load_teams=True,
            load_drafts=False,
            load_players=False,
            load_brackets=False,
        )
        if event is None:
            raise NotFoundException(f"Event {draft.event_id} not found")

        if not is_same_server(cmd.access_data, event.server_id):
            raise ForbiddenException("Event belongs to a different server")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can choose team formation variant")

        if draft.status not in (DraftStatus.BALANCE_REQUESTED, DraftStatus.OPEN):
            raise ConflictException(f"Draft status is {draft.status.value}, cannot select variant")

        job = await self._variant_store.get_latest_by_draft(draft.event_id, cmd.draft_id)
        if job is None:
            raise NotFoundException("Team formation job expired or not found, run team formation again")

        if job.status == "pending":
            raise ConflictException("Team formation is still in progress, wait for completion before selecting a variant")

        selected = None
        for v in job.variants:
            if v.id == cmd.variant_id:
                selected = v
                break

        if selected is None:
            raise NotFoundException(f"Variant {cmd.variant_id} not found in cached job")

        if not selected.teams:
            raise ConflictException("Selected variant has no teams")

        created_teams: list[TeamDetail] = []
        role_ids = {role.id for role in (event.selected_game_roles or [])}
        for vt in selected.teams:
            team = await self._team_repo.create(TeamCreate(
                event_id=draft.event_id,
                draft_id=cmd.draft_id,
                name=vt.name,
            ))
            for i, ep_id in enumerate(vt.event_player_ids):
                role_id = vt.game_role_ids[i] if i < len(vt.game_role_ids) else _get_first_role(event)
                if role_id not in role_ids:
                    raise BadRequestException(f"Unknown game role in selected variant: {role_id}")
                rating_val = vt.calculated_ratings[i] if i < len(vt.calculated_ratings) else 1000.0
                mid = vt.member_ids[i] if i < len(vt.member_ids) else ep_id
                await self._team_player_repo.create(TeamPlayerCreate(
                    team_id=team.id,
                    member_id=mid,
                    game_role_id=role_id,
                    rating=rating_val,
                ))
                await self._player_repo.update(ep_id, EventPlayerUpdate(status=EventPlayerStatus.SELECTED))
            loaded = await self._team_repo.get(team.id, load_event=False, load_players=True)
            if loaded:
                created_teams.append(TeamDetail.model_validate(loaded))

        await self._draft_repo.update(DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_SELECTED))
        await self._variant_store.delete(job.job_id, draft.event_id, cmd.draft_id)

        return created_teams

    def _build_mix_balancer_request(
        self, event, balancer_players: list[BalancerPlayer], cmd
    ) -> tuple[MixBalanceSettings, list[BalancerPlayer]]:
        team_size = event.team_size or 2
        settings = MixBalanceSettings(
            max_in_team=team_size,
            roles={
                role.id: MixRoleConfig(
                    max_in_team=(role.override_min_count or 1) if team_size > 1 else 0,
                    min_in_team=(role.override_min_count or 1) if team_size > 1 else 0,
                )
                for role in (event.selected_game_roles or [])
            },
        )
        normalized = self._normalize_priorities_for_mix(balancer_players)
        return settings, normalized

    def _build_tournament_balancer_request(
        self, event, balancer_players: list[BalancerPlayer], cmd
    ) -> tuple[TournamentBalanceSettings, list[BalancerPlayer]]:
        team_count = cmd.team_count or (len(balancer_players) // event.team_size if event.team_size else 0)
        if team_count < 2:
            raise BadRequestException("Tournament requires at least 2 teams")
        settings = TournamentBalanceSettings(
            team_count=team_count,
            players_in_team=event.team_size,
            roles={
                role.id: TournamentRoleConfig(
                    count_in_team=(role.override_min_count or 1) if event.team_size > 1 else 0,
                )
                for role in (event.selected_game_roles or [])
            },
            priority={"max_priority": 100},
        )
        normalized = self._normalize_priorities_for_tournament(balancer_players, max_priority=100)
        return settings, normalized

    def _build_balancer_players(
        self, players_with_roles, rating_snapshot: list[RatingSnapshotPlayerFull]
    ) -> list[BalancerPlayer]:
        rs_index = {}
        for r in rating_snapshot:
            rs_index[(r.member_id, r.game_role_id)] = r

        member_roles: dict[UUID, dict[UUID, BalancerPlayerRole]] = {}
        for player in players_with_roles:
            for role in (player.player_roles or []):
                rs = rs_index.get((player.member_id, role.game_role_id))
                calculated_rating = rs.calculated_rating if rs else 1000.0
                if player.member_id not in member_roles:
                    member_roles[player.member_id] = {}
                member_roles[player.member_id][role.game_role_id] = BalancerPlayerRole(
                    priority=role.priority,
                    rating=int(round(calculated_rating)),
                )

        return [
            BalancerPlayer(member_id=mid, roles=roles)
            for mid, roles in member_roles.items()
        ]

    async def _build_rating_snapshot(self, draft, event, cmd: RunTeamFormationCommand) -> list[RatingSnapshotPlayerFull]:
        snapshot: list[RatingSnapshotPlayerFull] = []
        selected_role_ids = {role.id for role in (event.selected_game_roles or [])}
        role_id_map = {}
        for role in (event.selected_game_roles or []):
            role_id_map[role.id] = role.id
            role_id_map[role.game_role_id] = role.id
        draft_player_ids = {dp.event_player_id for dp in draft.drafted_players}

        command_snapshot = cmd.rating_snapshot
        if command_snapshot:
            for item in command_snapshot:
                selected_role_id = role_id_map.get(item.game_role_id)
                if selected_role_id is None:
                    raise BadRequestException(f"Unknown game role in rating snapshot: {item.game_role_id}")
                event_player_id = item.event_player_id
                if event_player_id is None:
                    event_player_id = await self._resolve_event_player_id(draft_player_ids, item.member_id)
                if event_player_id not in draft_player_ids:
                    raise BadRequestException(f"Rating snapshot player is not in draft: {event_player_id}")
                player = await self._player_repo.get(event_player_id, load_roles=True, load_drafted=False)
                player_role_ids = {role.game_role_id for role in (player.player_roles if player else [])}
                if selected_role_id not in player_role_ids:
                    raise BadRequestException(
                        f"Rating snapshot role {selected_role_id} is not selected by player {event_player_id}"
                    )
                snapshot.append(            RatingSnapshotPlayerFull(
                    member_id=item.member_id,
                    event_player_id=event_player_id,
                    game_role_id=selected_role_id,
                    priority=item.priority,
                    open_rating=item.open_rating,
                    calculated_rating=item.open_rating,
                    rating_source="open",
                ))

        for dp in draft.drafted_players:
            player = await self._player_repo.get(dp.event_player_id, load_roles=True, load_drafted=False)
            if player is None:
                continue
            for role in (player.player_roles or []):
                if role.game_role_id not in selected_role_ids:
                    continue
                if any(s.event_player_id == player.id and s.game_role_id == role.game_role_id for s in snapshot):
                    continue
                open_rating = 1000.0
                snapshot.append(            RatingSnapshotPlayerFull(
                    member_id=player.member_id,
                    event_player_id=player.id,
                    game_role_id=role.game_role_id,
                    priority=role.priority,
                    open_rating=open_rating,
                    calculated_rating=open_rating,
                    rating_source="open",
                ))

        if cmd.use_effective_rating and event.rating_set_id and snapshot:
            try:
                rating_players = [
                    RatingPlayerRequest(
                        member_id=s.member_id,
                        role_id=s.game_role_id,
                        open_rating=s.open_rating,
                        priority=s.priority,
                    )
                    for s in snapshot
                ]
                rating_settings = cmd.rating_settings
                effective = await self._rating_client.calculate_effective_ratings(
                    draft_id=draft.id,
                    players=rating_players,
                    settings=rating_settings,
                )
                eff_map = {}
                for e in effective:
                    eff_map[(e.member_id, e.role_id)] = e.effective_rating
                for s in snapshot:
                    eff = eff_map.get((s.member_id, s.game_role_id))
                    if eff is not None:
                        s.effective_rating = float(eff)
                        s.calculated_rating = float(eff)
                        s.rating_source = "effective"
            except Exception as exc:
                raise BadRequestException(f"Failed to calculate effective ratings: {exc}") from exc

        return snapshot

    async def _resolve_event_player_id(self, draft_player_ids: set[UUID], member_id: UUID) -> UUID:
        for event_player_id in draft_player_ids:
            player = await self._player_repo.get(event_player_id, load_roles=False, load_drafted=False)
            if player and player.member_id == member_id:
                return player.id
        raise BadRequestException(f"Rating snapshot member is not in draft: {member_id}")

    def _normalize_priorities_for_mix(self, players: list[BalancerPlayer]) -> list[BalancerPlayer]:
        return self._normalize_priorities(players, lambda value: max(1, value))

    def _normalize_priorities_for_tournament(self, players: list[BalancerPlayer], max_priority: int) -> list[BalancerPlayer]:
        return self._normalize_priorities(players, lambda value: max(1, min(max_priority, max_priority + 1 - value)))

    def _normalize_priorities(self, players: list[BalancerPlayer], normalize) -> list[BalancerPlayer]:
        normalized = []
        for player in players:
            roles = {}
            for role_id, role_data in player.roles.items():
                roles[role_id] = BalancerPlayerRole(
                    priority=normalize(role_data.priority),
                    rating=role_data.rating,
                )
            normalized.append(BalancerPlayer(
                member_id=player.member_id,
                roles=roles,
            ))
        return normalized

    def _extract_team_players(
        self,
        team: BalancerTeam,
        event_player_by_member: dict[UUID, UUID],
        role_by_member: dict[UUID, UUID],
    ) -> tuple[list[UUID], list[UUID], list[UUID], list[float]]:
        member_ids = []
        event_player_ids = []
        game_role_ids = []
        calculated_ratings = []
        for player in team.players:
            member_ids.append(player.member_id)
            ep_id = event_player_by_member.get(player.member_id)
            if ep_id:
                event_player_ids.append(ep_id)
            role_id = player.game_role_id or role_by_member.get(player.member_id)
            if role_id:
                game_role_ids.append(role_id)
            calculated_ratings.append(float(player.rating))
        return member_ids, event_player_ids, game_role_ids, calculated_ratings
