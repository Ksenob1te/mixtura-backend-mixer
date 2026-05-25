# TeamFormationService — Business Logic

## Overview
- **File:** `src/core/services/team_formation.py`
- **Private helpers:** `_get_first_role(event)`, `_build_rating_snapshot()`, `_build_balancer_players()`, `_build_mix_balancer_request()`, `_build_tournament_balancer_request()`, `_resolve_event_player_id()`, `_normalize_priorities()`, `_normalize_priorities_for_mix()`, `_normalize_priorities_for_tournament()`, `_extract_team_players()`

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события
- `OrganizerRepositoryProtocol` — не используется напрямую (проверка через event.organizers)
- `DraftRepositoryProtocol` — CRUD Draft, загрузка с drafted_players
- `PlayerRepositoryProtocol` — загрузка EventPlayer с roles, update status
- `TeamRepositoryProtocol` — создание Team, загрузка с players
- `TeamPlayerRepositoryProtocol` — создание TeamPlayer

### Clients
- `RatingClientProtocol` — `calculate_effective_ratings()` (неблокирующий RabbitMQ RPC)
- `BalancerRequestRepositoryProtocol` — `request_mix_formation()`, `request_tournament_formation()` (publish, не RPC)

### Stores
- `TeamFormationVariantStoreProtocol` — Redis кэш вариантов (TTL из `env.team_formation_variants_ttl_seconds`)
- `BalancerTaskStoreProtocol` — Redis хранилище контекста задач балансировки

## Method: `run(cmd: RunTeamFormationCommand) -> TeamFormationJob`

### Purpose
Запуск автоматической балансировки команд. Создаёт задачу в Redis, публикует запрос балансеру через RabbitMQ (publish, не RPC), сразу возвращает job со статусом "pending". Результаты приходят асинхронно через handler и `complete_formation()`.

### Algorithm
1. Загрузка draft с drafted_players → `NotFoundException`
2. Загрузка event с organizers, game_roles, teams → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. Проверка draft.status in (OPEN, BALANCE_REQUESTED) → `ConflictException`
   - Если BALANCE_REQUESTED: проверка что job не pending → `ConflictException` ("Team formation is still in progress...")
6. Проверка event.team_formation == BALANCE → `BadRequestException`
7. **Build rating snapshot:**
   - Если передан `cmd.rating_snapshot`: валидация ролей и игроков → `BadRequestException`
   - Для всех drafted_players: добавление с open_rating=1000.0
   - Если `use_effective_rating` и `rating_set_id`: вызов `rating_client.calculate_effective_ratings()` → `BadRequestException` при ошибке
8. **Build balancer players:** группировка ролей по member_id с priority и rating
9. **Создание задачи:**
   - `BalancerTask` в `BalancerTaskStore` (status="pending", event_player_by_member, role_by_member, rating_snapshot)
   - `TeamFormationJob(status="pending")` в `TeamFormationVariantStore`
10. **Публикация запроса балансеру:**
    - Если TOURNAMENT → `balancer_repo.request_tournament_formation()` (нужен team_count >= 2 → `BadRequestException`)
    - Иначе → `balancer_repo.request_mix_formation()`
    - Публикация с `correlation_id=task_id`, `reply_to="mixer_service.balancer.result"`
11. Обновление draft.status = BALANCE_REQUESTED
12. Возврат pending job

### Balancer Settings Models

**Mix:**
```python
MixBalanceSettings(
    max_in_team: int,
    roles: dict[UUID, MixRoleConfig]  # role_id -> {max_in_team, min_in_team}
)
# MixRoleConfig.max_in_team == MixRoleConfig.min_in_team (фиксированный слот роли в команде)
```

**Tournament:**
```python
TournamentBalanceSettings(
    team_count: int,
    players_in_team: int,
    roles: dict[UUID, TournamentRoleConfig],  # role_id -> {count_in_team: int}
    priority: dict[str, int]                # {"max_priority": int}
)
```

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft статус не OPEN и не BALANCE_REQUESTED |
| `ConflictException` | Job ещё в процессе (pending) при re-run |
| `BadRequestException` | team_formation не BALANCE |
| `BadRequestException` | Unknown game role в rating_snapshot |
| `BadRequestException` | Игрок из snapshot не в draft |
| `BadRequestException` | Роль из snapshot не выбрана игроком |
| `BadRequestException` | Ошибка effective rating |
| `BadRequestException` | Tournament requires >= 2 teams |

---

## Method: `complete_formation(task_id: UUID, result: MixBalancerResult | TournamentBalancerResult) -> None`

### Purpose
Вызывается handler'ом при получении результата балансировки. Разбирает `BalancerResponse`, читает контекст задачи из Redis, строит варианты, сохраняет завершённый `TeamFormationJob`.

### Algorithm
1. Получение `BalancerTask` из `BalancerTaskStore` по `task_id` → выход если нет
2. Итерация по `result.balances`:
   - Извлечение команд через `BalancerTeam.players` → `BalancerTeamPlayer` (member_id, game_role_id, rating)
   - `event_player_id` восстанавливается из `event_player_by_member` по `member_id`
   - Построение `TeamFormationVariant` с `metrics=balance.quality` (оригинальные `MixQualityMetrics` или `TournamentQualityMetrics`)
3. Создание `TeamFormationJob(status="completed")`
4. Сохранение в `TeamFormationVariantStore`
5. Удаление `BalancerTask` из `BalancerTaskStore`

---

## Method: `get(cmd: GetTeamFormationCommand) -> TeamFormationJob`

### Purpose
Получение результатов последней балансировки из Redis кэша. Возвращает как pending (ещё в процессе), так и completed job.

### Algorithm
1. Загрузка draft → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. `variant_store.get_latest_by_draft(event_id, draft_id)` → `NotFoundException` если нет
6. Пагинация variants: `offset = (page-1)*page_size`, возврат slice
7. Возврат job с пагинированными variants

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Нет доступа |
| `NotFoundException` | Job не найден или истёк |

---

## Method: `choose_variant(cmd: ChooseTeamFormationVariantCommand) -> list[TeamDetail]`

### Purpose
Выбор варианта балансировки и создание команд в БД.

### Algorithm
1. Загрузка draft с drafted_players → `NotFoundException`
2. Загрузка event с organizers, game_roles, teams → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. Проверка draft.status в (BALANCE_REQUESTED, OPEN) → `ConflictException`
6. `variant_store.get_latest_by_draft(event_id, draft_id)` → `NotFoundException`
7. Проверка job.status == "pending" → `ConflictException` ("still in progress")
8. Поиск variant по variant_id → `NotFoundException`
9. Проверка variant.teams не пустой → `ConflictException`
10. Для каждой команды в варианте:
    - Создание Team
    - Для каждого игрока: проверка game_role в selected_game_roles → `BadRequestException`
    - Создание TeamPlayer (member_id, game_role_id, rating)
    - Обновление EventPlayer.status = SELECTED
11. Обновление draft.status = BALANCE_SELECTED
12. Удаление job из Redis
13. Возврат созданных команд

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft статус не BALANCE_REQUESTED/OPEN |
| `NotFoundException` | Job истёк |
| `ConflictException` | Formation ещё в процессе (pending) |
| `NotFoundException` | Variant не найден |
| `ConflictException` | Вариант без команд |
| `BadRequestException` | Unknown game role в варианте |
