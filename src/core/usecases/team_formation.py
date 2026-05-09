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
from src.core.models.draft import DraftStatus, DraftUpdate
from src.core.models.event_player import EventPlayerStatus, EventPlayerUpdate
from src.core.models.event import EventMatchType, TeamFormation as TeamFormationMethod
from src.core.models.team import Team, TeamCreate
from src.core.models.team_player import TeamPlayerCreate
from src.core.results.team_formation import (
    TeamFormationJob,
    TeamFormationVariant,
    TeamFormationVariantTeam,
    TeamFormationVariantMetrics,
    RatingSnapshotPlayer,
)
from src.core.usecases._access import (
    P_EVENT_ADMIN_MANAGE_BRACKET,
    has_event_admin_permission,
    has_server_ban,
    is_same_server,
)


class RunTeamFormationUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol,
                 draft_repo: DraftRepositoryProtocol, player_repo: PlayerRepositoryProtocol,
                 team_repo: TeamRepositoryProtocol, variant_store, rating_client, mix_balancer_client,
                 tournament_balancer_client, env):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._draft_repo = draft_repo
        self._player_repo = player_repo
        self._team_repo = team_repo
        self._variant_store = variant_store
        self._rating_client = rating_client
        self._mix_balancer = mix_balancer_client
        self._tournament_balancer = tournament_balancer_client
        self._env = env

    async def __call__(self, cmd: RunTeamFormationCommand) -> TeamFormationJob:
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
            raise ForbiddenException("Only organizer or admin can run team formation")

        if has_server_ban(cmd.access_data):
            raise ForbiddenException("Server ban restriction applies")

        if draft.status != DraftStatus.OPEN:
            raise ConflictException(f"Draft is not OPEN (status={draft.status.value})")

        if event.team_formation != TeamFormationMethod.BALANCE:
            raise BadRequestException(f"Event team formation method is {event.team_formation.value}, not BALANCE")

        rating_snapshot = await self._build_rating_snapshot(draft, event, cmd)

        job_id = uuid.uuid4()

        players_with_roles = []
        for dp in draft.drafted_players:
            player = await self._player_repo.get(dp.event_player_id, load_roles=True, load_drafted=False)
            if player:
                players_with_roles.append(player)

        balancer_players = self._build_balancer_players(players_with_roles, rating_snapshot)
        event_player_by_member = {player.member_id: player.id for player in players_with_roles}
        role_by_member = {item.member_id: item.game_role_id for item in rating_snapshot}

        if event.match_type == EventMatchType.TOURNAMENT:
            raw_variants = await self._call_tournament_balancer(
                cmd.draft_id, event, balancer_players, cmd
            )
        else:
            raw_variants = await self._call_mix_balancer(
                cmd.draft_id, event, balancer_players, cmd
            )

        variants = []
        for i, rv in enumerate(raw_variants):
            variant_id = uuid.uuid4()
            teams_data = rv.get("teams", [])
            variant_teams = []
            for ti, td in enumerate(teams_data):
                member_ids, event_player_ids, game_role_ids, calculated_ratings = self._extract_team_players(
                    td, event_player_by_member, role_by_member,
                )
                variant_teams.append(TeamFormationVariantTeam(
                    team_index=ti,
                    name=td.get("name", f"Team {ti + 1}"),
                    member_ids=member_ids,
                    event_player_ids=event_player_ids,
                    game_role_ids=game_role_ids,
                    calculated_ratings=calculated_ratings,
                ))
            metrics = TeamFormationVariantMetrics(
                strength_diff=rv.get("quality_uniformity", rv.get("dp_fairness", 0.0)),
                role_fit=rv.get("quality_role_fairness", 0.0),
                rating_spread=rv.get("vq_uniformity", 0.0),
                constraint_violations=rv.get("constraint_violations", 0),
                raw_metrics={k: float(v) for k, v in rv.items() if isinstance(v, (int, float))},
            )
            variants.append(TeamFormationVariant(
                id=variant_id,
                draft_id=cmd.draft_id,
                teams=variant_teams,
                metrics=metrics,
            ))

        job = TeamFormationJob(
            job_id=job_id,
            draft_id=cmd.draft_id,
            event_id=draft.event_id,
            status="completed",
            variants=variants,
            rating_snapshot=rating_snapshot,
        )

        ttl = self._env.team_formation_variants_ttl_seconds
        await self._variant_store.save(job_id, draft.event_id, cmd.draft_id, job, ttl)

        await self._draft_repo.update(DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_REQUESTED))

        return job

    async def _call_mix_balancer(self, draft_id, event, balancer_players, cmd):
        team_size = event.team_size or 2
        balancer_settings = {
            "min_in_team": 1,
            "max_in_team": team_size,
            "roles": {
                str(role.id): {"count_in_team": (role.override_min_count or 1) if team_size > 1 else 0}
                for role in (event.selected_game_roles or [])
            },
        }
        return await self._mix_balancer.balance(
            draft_id=draft_id,
            players=self._normalize_priorities_for_mix(balancer_players),
            balance_settings=balancer_settings,
        )

    async def _call_tournament_balancer(self, draft_id, event, balancer_players, cmd):
        team_count = cmd.team_count or (len(balancer_players) // event.team_size if event.team_size else 0)
        if team_count < 2:
            raise BadRequestException("Tournament requires at least 2 teams")
        balancer_settings = {
            "team_count": team_count,
            "players_in_team": event.team_size,
            "roles": {
                str(role.id): {
                    "count_in_team": (role.override_min_count or 1) if event.team_size > 1 else 0,
                    "min_count_in_team": role.override_min_count or 0,
                    "max_count_in_team": role.override_max_count or event.team_size,
                }
                for role in (event.selected_game_roles or [])
            },
            "priority": {"max_priority": 100},
        }
        return await self._tournament_balancer.balance(
            draft_id=draft_id,
            players=self._normalize_priorities_for_tournament(balancer_players, max_priority=100),
            balance_settings=balancer_settings,
        )

    def _build_balancer_players(self, players_with_roles, rating_snapshot):
        rs_index = {}
        for r in rating_snapshot:
            rs_index[(r.member_id, r.game_role_id)] = r

        member_roles = {}
        for player in players_with_roles:
            for role in (player.player_roles or []):
                if player.member_id not in member_roles:
                    member_roles[player.member_id] = {}
                rs = rs_index.get((player.member_id, role.game_role_id))
                calculated_rating = rs.calculated_rating if rs else 1000.0
                member_roles[player.member_id][str(role.game_role_id)] = {
                    "priority": role.priority,
                    "rating": int(round(calculated_rating)),
                }

        return [
            {"member_id": str(mid), "roles": roles}
            for mid, roles in member_roles.items()
        ]

    async def _build_rating_snapshot(self, draft, event, cmd: RunTeamFormationCommand) -> list[RatingSnapshotPlayer]:
        snapshot: list[RatingSnapshotPlayer] = []
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
                snapshot.append(RatingSnapshotPlayer(
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
                snapshot.append(RatingSnapshotPlayer(
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
                    {
                        "member_id": str(s.member_id),
                        "role_id": str(s.game_role_id),
                        "open_rating": s.open_rating,
                        "priority": s.priority,
                    }
                    for s in snapshot
                ]
                effective = await self._rating_client.calculate_effective_ratings(
                    draft_id=draft.id,
                    players=rating_players,
                    settings=cmd.rating_settings or ({"rating_set_id": str(event.rating_set_id)} if event.rating_set_id else None),
                )
                eff_map = {}
                for e in effective:
                    member_id = self._read_uuid(e, "member_id")
                    rid = self._read_uuid(e, "role_id")
                    effective_rating = self._read_float(e, "effective_rating")
                    if member_id is not None and rid is not None and effective_rating is not None:
                        eff_map[(member_id, rid)] = effective_rating
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

    def _normalize_priorities_for_mix(self, players: list[dict]) -> list[dict]:
        return self._normalize_priorities(players, lambda value: max(1, value))

    def _normalize_priorities_for_tournament(self, players: list[dict], max_priority: int) -> list[dict]:
        return self._normalize_priorities(players, lambda value: max(1, min(max_priority, max_priority + 1 - value)))

    def _normalize_priorities(self, players: list[dict], normalize):
        normalized = []
        for player in players:
            roles = {}
            for role_id, role_data in player.get("roles", {}).items():
                data = dict(role_data)
                data["priority"] = normalize(int(data.get("priority", 1)))
                roles[role_id] = data
            normalized.append({**player, "roles": roles})
        return normalized

    def _extract_team_players(
        self,
        team_data: dict,
        event_player_by_member: dict[UUID, UUID],
        role_by_member: dict[UUID, UUID],
    ) -> tuple[list[UUID], list[UUID], list[UUID], list[float]]:
        raw_players = team_data.get("players")
        if isinstance(raw_players, list) and raw_players:
            member_ids = []
            event_player_ids = []
            game_role_ids = []
            calculated_ratings = []
            for player in raw_players:
                member_id = self._read_uuid(player, "member_id")
                event_player_id = self._read_uuid(player, "event_player_id")
                if event_player_id is None and member_id is not None:
                    event_player_id = event_player_by_member.get(member_id)
                role_id = self._read_uuid(player, "game_role_id") or self._read_uuid(player, "role_id")
                if role_id is None and member_id is not None:
                    role_id = role_by_member.get(member_id)
                rating = self._read_float(player, "calculated_rating")
                if rating is None:
                    rating = self._read_float(player, "rating") or 0.0
                if member_id is not None:
                    member_ids.append(member_id)
                if event_player_id is not None:
                    event_player_ids.append(event_player_id)
                if role_id is not None:
                    game_role_ids.append(role_id)
                calculated_ratings.append(rating)
            return member_ids, event_player_ids, game_role_ids, calculated_ratings

        raw_member_ids = team_data.get("member_ids", [])
        member_ids = [UUID(m) if isinstance(m, str) else m for m in raw_member_ids]
        raw_ep_ids = team_data.get("event_player_ids", [])
        event_player_ids = [UUID(e) if isinstance(e, str) else e for e in raw_ep_ids]
        if not event_player_ids:
            event_player_ids = [event_player_by_member[m] for m in member_ids if m in event_player_by_member]
        raw_role_ids = team_data.get("game_role_ids", team_data.get("role_ids", []))
        game_role_ids = [UUID(g) if isinstance(g, str) else g for g in raw_role_ids]
        if not game_role_ids:
            game_role_ids = [role_by_member[m] for m in member_ids if m in role_by_member]
        calculated_ratings = [float(v) for v in team_data.get("calculated_ratings", team_data.get("ratings", []))]
        return member_ids, event_player_ids, game_role_ids, calculated_ratings

    def _read_uuid(self, data, key: str) -> UUID | None:
        value = data.get(key) if isinstance(data, dict) else getattr(data, key, None)
        if value is None:
            return None
        return UUID(str(value)) if isinstance(value, str) else value

    def _read_float(self, data, key: str) -> float | None:
        value = data.get(key) if isinstance(data, dict) else getattr(data, key, None)
        return None if value is None else float(value)


class GetTeamFormationUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol,
                 draft_repo: DraftRepositoryProtocol, variant_store):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._draft_repo = draft_repo
        self._variant_store = variant_store

    async def __call__(self, cmd: GetTeamFormationCommand) -> TeamFormationJob:
        draft = await self._draft_repo.get(cmd.draft_id, load_drafted_players=False)
        if draft is None:
            raise NotFoundException(f"Draft {cmd.draft_id} not found")

        if cmd.access_data is not None:
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


class ChooseTeamFormationVariantUseCase:
    def __init__(self, event_repo: EventRepositoryProtocol, organizer_repo: OrganizerRepositoryProtocol,
                 draft_repo: DraftRepositoryProtocol, team_repo: TeamRepositoryProtocol,
                 team_player_repo: TeamPlayerRepositoryProtocol, player_repo: PlayerRepositoryProtocol,
                 variant_store):
        self._event_repo = event_repo
        self._organizer_repo = organizer_repo
        self._draft_repo = draft_repo
        self._team_repo = team_repo
        self._team_player_repo = team_player_repo
        self._player_repo = player_repo
        self._variant_store = variant_store

    async def __call__(self, cmd: ChooseTeamFormationVariantCommand) -> list[Team]:
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
        if has_server_ban(cmd.access_data):
            raise ForbiddenException("Server ban restriction applies")
        is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)
        is_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_MANAGE_BRACKET)
        if not is_organizer and not is_admin:
            raise ForbiddenException("Only organizer or admin can choose team formation variant")

        if draft.status not in (DraftStatus.BALANCE_REQUESTED, DraftStatus.OPEN):
            raise ConflictException(f"Draft status is {draft.status.value}, cannot select variant")

        job = await self._variant_store.get_latest_by_draft(draft.event_id, cmd.draft_id)
        if job is None:
            raise NotFoundException("Team formation job expired or not found, run team formation again")

        selected = None
        for v in job.variants:
            if v.id == cmd.variant_id:
                selected = v
                break

        if selected is None:
            raise NotFoundException(f"Variant {cmd.variant_id} not found in cached job")

        if not selected.teams:
            raise ConflictException("Selected variant has no teams")

        created_teams: list[Team] = []
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
                created_teams.append(loaded)

        await self._draft_repo.update(DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_SELECTED))
        await self._variant_store.delete(job.job_id, draft.event_id, cmd.draft_id)

        return created_teams


def _get_first_role(event):
    roles = event.selected_game_roles
    if roles:
        return roles[0].id
    return uuid.uuid4()
