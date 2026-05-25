# Team Formation — Queue Contracts

## Overview
- **Handler files:** `src/infra/rabbit/api/team_formation.py`, `src/infra/rabbit/api/balancer_result.py`
- **Service file:** `src/core/services/team_formation.py`
- **Commands file:** `src/core/commands/team_formation.py`
- **Results files:** `src/core/results/team_formation.py`, `src/core/results/team.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.team_formation.run` | `RunTeamFormationCommand` | `TeamFormationJob` | Запуск балансировки команд (возвращает pending) |
| `event.team_formation.get` | `GetTeamFormationCommand` | `TeamFormationJob` | Получение результатов балансировки |
| `event.team_formation.choose` | `ChooseTeamFormationVariantCommand` | `list[TeamDetail]` | Выбор варианта и создание команд |
| `mixer_service.balancer.result` | `BalancerResponse` | — | Handler для результатов балансировки (internal) |

---

## Queue: `event.team_formation.run`

### Command: `RunTeamFormationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `draft_id` | `UUID` | Yes | ID draft-сессии |
| `use_effective_rating` | `bool` | No | Использовать effective rating (default: False) |
| `rating_snapshot` | `list[RatingSnapshotInput]` | No | Кастомный snapshot рейтингов |
| `rating_settings` | `RatingSettings \| None` | No | Настройки для rating client |
| `team_count` | `int \| None` | No | Количество команд (для tournament) |

**RatingSnapshotInput:** `member_id` (UUID), `event_player_id` (UUID|None), `game_role_id` (UUID), `priority` (int, default 1), `open_rating` (float)

### Result: `TeamFormationJob`
| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `UUID` | ID задачи |
| `draft_id` | `UUID` | |
| `event_id` | `UUID` | |
| `status` | `str` | "pending" или "completed" |
| `variants` | `list[TeamFormationVariant]` | Варианты распределения (пустой для pending) |
| `rating_snapshot` | `list[RatingSnapshotPlayer]` | Snapshot рейтингов |
| `error` | `str \| None` | Ошибка если была |

**TeamFormationVariant:** `id` (UUID), `draft_id` (UUID), `teams` (list[TeamFormationVariantTeam]), `metrics` (MixQualityMetrics | TournamentQualityMetrics — см. [Balancer Models](#queue-mixer_servicebalancerresult-internal)), `is_selected` (bool)

**TeamFormationVariantTeam:** `team_index` (int), `name` (str), `member_ids` (list[UUID]), `event_player_ids` (list[UUID]), `game_role_ids` (list[UUID]), `calculated_ratings` (list[float])

**RatingSnapshotPlayer:** `member_id` (UUID), `event_player_id` (UUID), `game_role_id` (UUID), `priority` (int), `open_rating` (float), `rating_source` (str)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft статус не OPEN и не BALANCE_REQUESTED |
| `ConflictException` | Job ещё в процессе (pending) при re-run |
| `BadRequestException` | `team_formation` не BALANCE |
| `BadRequestException` | Unknown game role в rating_snapshot |
| `BadRequestException` | Игрок из rating_snapshot не в draft |
| `BadRequestException` | Роль из rating_snapshot не выбрана игроком |
| `BadRequestException` | Ошибка effective rating calculation |

---

## Queue: `event.team_formation.get`

### Command: `GetTeamFormationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `draft_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `pagination` | `PaginationRequest` | No | Пагинация вариантов |

### Result: `TeamFormationJob`
Та же схема, что и в [`event.team_formation.run`](#queue-eventteam_formationrun). Возвращает job с пагинированными variants. Может быть в статусе "pending" (ещё в процессе) или "completed".

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | Нет доступа |
| `NotFoundException` | Job не найден или истёк (TTL) |

---

## Queue: `event.team_formation.choose`

### Command: `ChooseTeamFormationVariantCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `draft_id` | `UUID` | Yes | |
| `variant_id` | `UUID` | Yes | ID выбранного варианта |

### Result: `list[TeamDetail]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `draft_id` | `UUID \| None` | |
| `name` | `str` | |
| `players` | `list[TeamPlayerItem]` | Игроки команды |

**TeamPlayerItem:** `id` (UUID), `team_id` (UUID), `member_id` (UUID), `game_role_id` (UUID), `rating` (float)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft статус не BALANCE_REQUESTED или OPEN |
| `NotFoundException` | Job истёк или не найден |
| `ConflictException` | Formation ещё в процессе (pending) |
| `NotFoundException` | Variant не найден в job |
| `ConflictException` | Вариант не имеет команд |
| `BadRequestException` | Unknown game role в варианте |

---

## Queue: `mixer_service.balancer.result` (Internal)

Обрабатывает результаты от внешних балансеров (mix_balance_service, tournament_balance_service).

### Input: `BalancerResponse`
```python
BalancerResponse(
    status: int,
    message: MixBalancerResult | TournamentBalancerResult,
)
```

**MixBalancerResult:** `draft_id` (UUID), `balances` (list[MixBalance]), `created_at` (datetime)
- **MixBalance:** `id` (UUID), `quality` (MixQualityMetrics), `teams` (list[BalancerTeam])
- **MixQualityMetrics:** `uniformity` (float), `fairness` (float), `role_points` (float), `role_fairness` (float)

**TournamentBalancerResult:** `draft_id` (UUID), `balances` (list[TournamentBalance]), `created_at` (datetime)
- **TournamentBalance:** `id` (UUID), `quality` (TournamentQualityMetrics), `teams` (list[BalancerTeam])
- **TournamentQualityMetrics:** `dp_fairness` (float), `dp_role_fairness` (float), `vq_uniformity` (float), `role_priority_points` (float), `fitness_balance` (float), `fitness_priority` (float), `fitness_role_imbalance` (float), `fitness_team_spread` (float), `fitness_subrole` (float), `role_subrole_penalty` (float), `evaluation` (float)

**BalancerTeam:** `id` (UUID), `players` (list[BalancerTeamPlayer])

**BalancerTeamPlayer:** `member_id` (UUID), `game_role_id` (UUID), `rating` (int), `priority` (int, default 0)

Дискриминация: `MixQualityMetrics` — `extra='forbid'`, все поля обязательные → парсится при наличии `uniformity`. `TournamentQualityMetrics` — `extra='forbid'`, все поля с дефолтами → парсится при отсутствии `uniformity`.

Модели в `src/core/models/balancer.py`.

### Handler
`balancer_result_handler(body, correlation_id, service)`:
1. Извлекает `task_id = UUID(correlation_id)`
2. Парсит `body` как `BalancerResponse`
3. Вызывает `service.complete_formation(task_id, response.message)`

### Ошибки
Ошибки логируются, но не возвращаются отправителю (fire-and-forget). Если задача не найдена (истекла), результат игнорируется.
