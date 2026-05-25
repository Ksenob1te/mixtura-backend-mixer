# Balancer Model (DTOs for external balancer communication)

- **File:** `src/core/models/balancer.py`
- **Used by services:** `TeamFormationService`

## Role

DTO-модели для взаимодействия с внешними балансерами (`mix_balance_service`, `tournament_balance_service`) через RabbitMQ. Запросы отправляются через `BalancerRequestRepository`, ответы принимаются в `balancer_result_handler`. Не имеют ORM-отображения.

## Request Models (mixer → balancer)

### BalancerPlayerRole

Роль игрока в запросе балансировки.

| Field | Type | Description |
|-------|------|-------------|
| `priority` | `int` | Приоритет роли |
| `rating` | `int` | Рейтинг для роли |

### BalancerPlayer

Игрок в запросе балансировки.

| Field | Type | Description |
|-------|------|-------------|
| `member_id` | `UUID` | ID игрока |
| `roles` | `dict[UUID, BalancerPlayerRole]` | Роли игрока: game_role_id → данные |

### MixRoleConfig

Настройка слота роли для микс-балансировки.

| Field | Type | Description |
|-------|------|-------------|
| `max_in_team` | `int` | Максимум игроков этой роли в команде |
| `min_in_team` | `int` | Минимум игроков этой роли в команде |

### MixBalanceSettings

Настройки микс-балансировки.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_in_team` | `int` | — | Максимум игроков в команде |
| `roles` | `dict[UUID, MixRoleConfig]` | `{}` | Настройки ролей: role_id → конфигурация |

### TournamentRoleConfig

Настройка слота роли для турнирной балансировки.

| Field | Type | Description |
|-------|------|-------------|
| `count_in_team` | `int` | Количество игроков этой роли в команде |

### TournamentBalanceSettings

Настройки турнирной балансировки.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `team_count` | `int` | — | Количество команд |
| `players_in_team` | `int` | — | Игроков в одной команде |
| `roles` | `dict[UUID, TournamentRoleConfig]` | `{}` | Настройки ролей: role_id → конфигурация |
| `priority` | `dict[str, int]` | `{}` | Глобальные настройки приоритета (`{"max_priority": 100}`) |

## Response Models (balancer → mixer)

### BalancerTeamPlayer

Игрок в команде от балансера.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `member_id` | `UUID` | — | ID игрока |
| `game_role_id` | `UUID` | — | ID роли |
| `rating` | `int` | — | Рейтинг |
| `priority` | `int` | `0` | Приоритет (только tournament) |

### BalancerTeam

Команда в ответе балансера.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `UUID` | — | ID команды |
| `players` | `list[BalancerTeamPlayer]` | `[]` | Игроки команды |

### MixQualityMetrics (extra=forbid)

Метрики качества микс-балансировки.

| Field | Type | Description |
|-------|------|-------------|
| `uniformity` | `float` | Метрика равномерности |
| `fairness` | `float` | Метрика справедливости (DP) |
| `role_points` | `float` | Очки ролевого распределения |
| `role_fairness` | `float` | Справедливость ролей |

### TournamentQualityMetrics (extra=forbid)

Метрики качества турнирной балансировки. Все поля имеют default=`0.0`.

| Field | Type | Description |
|-------|------|-------------|
| `dp_fairness` | `float` | DP fairness |
| `dp_role_fairness` | `float` | DP role fairness |
| `vq_uniformity` | `float` | VQ uniformity |
| `role_priority_points` | `float` | Очки ролевого приоритета |
| `fitness_balance` | `float` | Фитнес баланса |
| `fitness_priority` | `float` | Фитнес приоритета |
| `fitness_role_imbalance` | `float` | Фитнес ролевого дисбаланса |
| `fitness_team_spread` | `float` | Фитнес разброса команд |
| `fitness_subrole` | `float` | Фитнес сабролей |
| `role_subrole_penalty` | `float` | Штраф сабролей |
| `evaluation` | `float` | Итоговая оценка |

### MixBalance

Вариант микс-балансировки.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `UUID` | — | ID варианта |
| `quality` | `MixQualityMetrics` | — | Метрики качества |
| `teams` | `list[BalancerTeam]` | `[]` | Команды |

### TournamentBalance

Вариант турнирной балансировки.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `UUID` | — | ID варианта |
| `quality` | `TournamentQualityMetrics` | — | Метрики качества |
| `teams` | `list[BalancerTeam]` | `[]` | Команды |

### MixBalancerResult

Ответ микс-балансера.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `draft_id` | `UUID` | — | ID драфта |
| `balances` | `list[MixBalance]` | `[]` | Варианты балансировки |
| `created_at` | `datetime` | `now()` | Время создания |

### TournamentBalancerResult

Ответ турнирного балансера.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `draft_id` | `UUID` | — | ID драфта |
| `balances` | `list[TournamentBalance]` | `[]` | Варианты балансировки |
| `created_at` | `datetime` | `now()` | Время создания |

### BalancerResponse

Обёртка ответа балансера (`ResponseMessage`).

| Field | Type | Description |
|-------|------|-------------|
| `status` | `int` | HTTP-статус (200) |
| `message` | `MixBalancerResult \| TournamentBalancerResult` | Тело ответа |

### Дискриминация

`MixQualityMetrics` — `extra='forbid'`, все поля обязательные → парсится при наличии `uniformity`.
`TournamentQualityMetrics` — `extra='forbid'`, все поля с дефолтами → парсится при отсутствии `uniformity`.
