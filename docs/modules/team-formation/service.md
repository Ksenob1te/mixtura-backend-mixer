# TeamFormationService — Business Logic

## Overview
- **File:** `src/core/services/team_formation.py`
- **Private helpers:** `_get_first_role(event)`, `_build_rating_snapshot()`, `_build_balancer_players()`, `_call_mix_balancer()`, `_call_tournament_balancer()`, `_normalize_priorities()`, `_extract_team_players()`, `_read_uuid()`, `_read_float()`

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события
- `OrganizerRepositoryProtocol` — не используется напрямую (проверка через event.organizers)
- `DraftRepositoryProtocol` — CRUD Draft, загрузка с drafted_players
- `PlayerRepositoryProtocol` — загрузка EventPlayer с roles, update status
- `TeamRepositoryProtocol` — создание Team, загрузка с players
- `TeamPlayerRepositoryProtocol` — создание TeamPlayer

### Clients
- `RatingClient` — `calculate_effective_ratings()` (RabbitMQ)
- `MixBalancerClient` — `balance()` для single match (RabbitMQ)
- `TournamentBalancerClient` — `balance()` для tournament (RabbitMQ)

### Stores
- `TeamFormationVariantStore` — Redis кэш вариантов (TTL из `env.team_formation_variants_ttl_seconds`)

## Method: `run(cmd: RunTeamFormationCommand) -> TeamFormationJob`

### Purpose
Запуск автоматической балансировки команд. Вызывает внешний balancer, сохраняет варианты в Redis, обновляет статус draft.

### Algorithm
1. Загрузка draft с drafted_players → `NotFoundException`
2. Загрузка event с organizers, game_roles, teams → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. Проверка draft.status == OPEN → `ConflictException`
6. Проверка event.team_formation == BALANCE → `BadRequestException`
7. **Build rating snapshot:**
   - Если передан `cmd.rating_snapshot`: валидация ролей и игроков → `BadRequestException`
   - Для всех drafted_players: добавление с open_rating=1000.0
   - Если `use_effective_rating` и `rating_set_id`: вызов `rating_client.calculate_effective_ratings()` → `BadRequestException` при ошибке
8. **Build balancer players:** группировка ролей по member_id с priority и rating
9. **Вызов balancer:**
   - Если TOURNAMENT → `_call_tournament_balancer()` (нужен team_count >= 2 → `BadRequestException`)
   - Иначе → `_call_mix_balancer()`
10. **Парсинг вариантов:** для каждого raw variant → TeamFormationVariant с teams, metrics
11. Создание `TeamFormationJob`
12. Сохранение в Redis через `variant_store.save(job_id, event_id, draft_id, job, ttl)`
13. Обновление draft.status = BALANCE_REQUESTED
14. Возврат job

### Balancer Settings

**Mix Balancer:**
```json
{
  "min_in_team": 1,
  "max_in_team": team_size,
  "roles": { "<role_id>": { "count_in_team": override_min_count or 1 } }
}
```

**Tournament Balancer:**
```json
{
  "team_count": team_count,
  "players_in_team": team_size,
  "roles": { "<role_id>": { "count_in_team": ..., "min_count_in_team": ..., "max_count_in_team": ... } },
  "priority": { "max_priority": 100 }
}
```

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft не OPEN |
| `BadRequestException` | team_formation не BALANCE |
| `BadRequestException` | Unknown game role в rating_snapshot |
| `BadRequestException` | Игрок из snapshot не в draft |
| `BadRequestException` | Роль из snapshot не выбрана игроком |
| `BadRequestException` | Ошибка effective rating |
| `BadRequestException` | Tournament requires >= 2 teams |

---

## Method: `get(cmd: GetTeamFormationCommand) -> TeamFormationJob`

### Purpose
Получение результатов последней балансировки из Redis кэша.

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

## Method: `choose_variant(cmd: ChooseTeamFormationVariantCommand) -> list[Team]`

### Purpose
Выбор варианта балансировки и создание команд в БД.

### Algorithm
1. Загрузка draft с drafted_players → `NotFoundException`
2. Загрузка event с organizers, game_roles, teams → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. Проверка draft.status в (BALANCE_REQUESTED, OPEN) → `ConflictException`
6. `variant_store.get_latest_by_draft(event_id, draft_id)` → `NotFoundException`
7. Поиск variant по variant_id → `NotFoundException`
8. Проверка variant.teams не пустой → `ConflictException`
9. Для каждой команды в варианте:
   - Создание Team
   - Для каждого игрока: проверка game_role в selected_game_roles → `BadRequestException`
   - Создание TeamPlayer (member_id, game_role_id, rating)
   - Обновление EventPlayer.status = SELECTED
10. Обновление draft.status = BALANCE_SELECTED
11. Удаление job из Redis
12. Возврат созданных команд

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft/Event не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `ConflictException` | Draft статус не BALANCE_REQUESTED/OPEN |
| `NotFoundException` | Job истёк |
| `NotFoundException` | Variant не найден |
| `ConflictException` | Вариант без команд |
| `BadRequestException` | Unknown game role в варианте |
