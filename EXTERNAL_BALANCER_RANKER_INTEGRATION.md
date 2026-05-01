# Интеграция с балансировщиками и рейтинг-сервисом

## Источники
- `C:/Users/dmela/Desktop/desktop/programming/mixtura_balance`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura_balancer_tournament`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura_ranker`

## Общий Поток Для Формирования Команд
- Модуль мероприятий не должен напрямую отправлять в балансировщик оценку из `custom`/экспертной оценки.
- Сначала модуль мероприятий собирает открытые оценки игроков по ролям и отправляет их в рейтинг-сервис на `rating.effective.calculate`.
- Рейтинг-сервис возвращает скорректированный `effective_rating` по каждой паре `member_id + role_id`.
- В балансировщик передается именно `effective_rating`, приведенный к `int`, в поле `PlayerRole.rating`.
- После выбора варианта баланса модуль мероприятий должен сохранить использованные рейтинги в `TeamPlayer.rating`, чтобы состав команды отражал снимок рейтинга на момент формирования.

## Rating Service
- Репозиторий: `mixtura_ranker`.
- FastStream app: `src/domain/main.py`.
- RabbitMQ broker: `RabbitBroker(env.rabbit.url)`.
- Ответы обернуты в `ResponseMessage[T]` с полями `status` и `message`.

### Очередь `rating.effective.calculate`
- Назначение: получить эффективные рейтинги для формирования команд.
- Handler: `src/domain/api/rating.py::calculate_effective_ratings`.
- Request model: `src/domain/models/requests.py::EffectiveRatingRequest`.
- Response model: `src/domain/models/responses.py::EffectiveRatingResponse`.

Request shape:
```python
EffectiveRatingRequest(
    draft_id=UUID,
    players=[
        Player(
            member_id=UUID,
            roles={
                role_id: PlayerRole(
                    priority=int,
                    open_rating=int,
                ),
            },
        ),
    ],
    settings=RatingSettings(...),
)
```

Response shape:
```python
EffectiveRatingResponse(
    draft_id=UUID,
    players=[
        PlayerEffectiveRating(
            member_id=UUID,
            role_id=UUID,
            open_rating=float,
            effective_rating=float,
            hidden_rating=float,
        ),
    ],
    created_at=datetime,
)
```

Integration notes:
- `open_rating` is the external/open rating supplied by the event module from organizer/player rating data.
- `effective_rating` is the only rating that should be sent to team balancers.
- `hidden_rating` in the response is the hidden rating projected back to the open scale; it is useful for diagnostics, not for direct balancing.
- If no hidden rating exists in the ranker DB, ranker derives one from the supplied `open_rating`.

### Очередь `rating.match.process`
- Назначение: обновить рейтинги после результата матча.
- Handler: `src/domain/api/rating.py::process_match_result`.
- Request model: `src/domain/models/requests.py::MatchResult`.
- Response model: `src/domain/models/responses.py::MatchResultResponse`.

Request shape:
```python
MatchResult(
    match_id=UUID,
    match_time=datetime,
    teams=[MatchTeam(team_id=UUID, player_ids=[UUID])],
    team_ranks=[1.0, 2.0],
    players=[
        MatchPlayer(
            member_id=UUID,
            role_id=UUID,
            open_rating=float,
        ),
    ],
    settings=RatingSettings(...),
)
```

Integration notes:
- `team_ranks` uses rank order, where `1.0` is first place. For a normal two-team match winner/loser is `[1.0, 2.0]`; draws should use equal ranks if supported by OpenSkill flow.
- `players` must contain every member referenced in `teams[*].player_ids`.
- `open_rating` should be the open rating snapshot for the player-role at match time, not an arbitrary current value.
- The rating service currently creates hidden rating rows only when none exist; verify persistence semantics before relying on full history updates.

## Mix Balance Service
- Репозиторий: `mixtura_balance`.
- Назначение: быстрый балансировщик для одиночного матча / двух команд.
- FastStream app: `src/balancer_service/app/main.py`.
- Queue: `mix_balance_service.balance`.
- Request model: `balancer_service.domain.models.balance_request.BalanceRequest`.
- Response model: `balancer_service.domain.models.balance.DraftBalances` wrapped in `ResponseMessage`.

Request shape:
```python
BalanceRequest(
    draft_id=UUID,
    players=[
        Player(
            member_id=UUID,
            roles={
                role_id: PlayerRole(
                    priority=int,
                    rating=int,  # effective rating from ranker
                ),
            },
        ),
    ],
    balance_settings=BalanceSettings(
        max_in_team=int,
        roles={
            role_id: RoleSettings(
                original_game_role=UUID,
                min_in_team=int,
                max_in_team=int,
            ),
        },
        math=MathSettings(...),
        balance_limit=float,
    ),
)
```

Response shape:
```python
DraftBalances(
    draft_id=UUID,
    balances=[
        Balance(
            id=UUID,
            quality=QualityMetrics(
                uniformity=float,
                fairness=float,
                role_points=float,
                role_fairness=float,
            ),
            teams=[
                Team(
                    id=UUID,
                    players=[TeamPlayer(member_id=UUID, game_role_id=UUID, rating=int)],
                ),
            ],
        ),
    ],
    created_at=datetime,
)
```

Validation and usage notes:
- `len(players)` must be at most `max_in_team * 2`; this service is for two-team balancing.
- All player role IDs must exist in `balance_settings.roles`.
- `min_in_team <= max_in_team`; sum of role minimums must not exceed `max_in_team`.
- Priority semantics in docs/examples are not fully consistent, but metrics docs describe lower priority value as better role preference. Normalize event-module role priorities before sending.

## Tournament Balance Service
- Репозиторий: `mixtura_balancer_tournament`.
- Назначение: турнирное формирование нескольких команд через NSGA-II.
- FastStream app: `src/mixtura_balancer_tournament/app/main.py`.
- Current handler queue in code: `tournament_balance_service.balance`.
- Progress queue in code: `mix_balance_service.balance.progress` with `correlation_id=str(draft_id)`.
- Warning: README/examples still mention `mix_balance_service.balance`; use `app/main.py` as source of truth or align queue names before integration.
- Request model: `mixtura_balancer_tournament.domain.models.balance_request.BalanceRequest`.
- Response model: `mixtura_balancer_tournament.domain.models.balance.DraftBalances` wrapped in `ResponseMessage`.

Request shape:
```python
BalanceRequest(
    draft_id=UUID,
    players=[
        Player(
            member_id=UUID,
            roles={
                role_id: PlayerRole(
                    priority=int,
                    rating=int,  # effective rating from ranker
                    subrole_ids=[UUID] | None,
                ),
            },
        ),
    ],
    balance_settings=BalanceSettings(
        players_in_team=int,
        roles={
            role_id: RoleSettings(
                original_game_role=UUID,
                count_in_team=int,
                subroles={subrole_id: SubroleSettings(capacity=int)},
            ),
        },
        priority=PrioritySettings(max_priority=int, power_coef=float),
        ranking=RankingSettings(...),
        balancing=BalancingSettings(...),
    ),
)
```

Response shape:
```python
DraftBalances(
    draft_id=UUID,
    balances=[
        Balance(
            id=UUID,
            quality=QualityMetrics(
                dp_fairness=float,
                dp_role_fairness=float,
                vq_uniformity=float,
                role_priority_points=float,
                fitness_balance=float,
                fitness_priority=float,
                fitness_role_imbalance=float,
                fitness_team_spread=float,
                fitness_subrole=float,
                role_subrole_penalty=float,
                evaluation=float,
            ),
            teams=[
                Team(
                    id=UUID,
                    total_rating=int,
                    players=[TeamPlayer(member_id=UUID, game_role_id=UUID, rating=int, priority=int)],
                ),
            ],
        ),
    ],
    created_at=datetime,
)
```

Progress shape:
```python
ResponseMessage(
    status=102,
    message=BalanceProgress(
        draft_id=UUID,
        processed_generations=int,
        total_generations=int,
        pareto_front_size=int,
        fitness_balance=ProgressMetricSummary(...),
        fitness_priority=ProgressMetricSummary(...),
        fitness_role_imbalance=ProgressMetricSummary(...),
        fitness_team_spread=ProgressMetricSummary(...),
        fitness_subrole=ProgressMetricSummary(...),
    ),
)
```

Validation and usage notes:
- `len(players)` must be divisible by `players_in_team`.
- Sum of all `RoleSettings.count_in_team` must exactly equal `players_in_team`.
- Player role priority must be `>= 1` and `<= priority.max_priority`.
- Tournament service describes higher priority value as higher preference. Normalize priorities separately from the mix balancer until both services share one convention.
- Optional subroles allow constraints inside a role, for example primary/secondary DPS; undefined subroles are rejected.

## Event Module Responsibilities
- Build the initial player-role snapshot from event players, selected roles and player role priorities.
- Fetch open role ratings from local event/custom data or the user-space/rating source decided by architecture.
- Call `rating.effective.calculate` and replace open ratings with `effective_rating` for all balancer requests.
- Select balancer by event/team-formation context:
- `mix_balance_service.balance` for two-team single-match balancing.
- `tournament_balance_service.balance` for tournament/team formation with multiple teams.
- Persist returned balance variants and quality metrics until organizer chooses one.
- Materialize the chosen balance into `Team` and `TeamPlayer`; store assigned `game_role_id`, `member_id`, and effective rating snapshot.
- After match completion, call `rating.match.process` with team ranks and player open-rating snapshots.
