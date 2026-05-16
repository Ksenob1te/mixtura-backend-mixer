# Rating Model (client DTOs)

- **File:** `src/core/models/rating.py`
- **Protocol:** `RatingClientProtocol`
- **Used by services:** `MatchService`, `TeamFormationService`

## Role

DTO-модели для взаимодействия с mixtura-ranker через RabbitMQ. Зеркалируют модели из `mixtura-ranker/src/domain/models/`. Не имеют ORM-отображения — используются только как контракт данных для RPC-клиента.

## Models

### RatingSettings

Параметры рейтинговой системы.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `r_min` | `float` | `0.0` | Минимальный открытый рейтинг |
| `r_max` | `float` | `5000.0` | Максимальный открытый рейтинг |
| `r_avg` | `float` | `2400.0` | Ожидаемый открытый рейтинг |
| `g` | `float` | `0.5` | Гравитация рейтинга игрока |
| `sigma_init` | `float` | `25.0` | Начальная неопределённость |
| `d` | `float` | `4.0` | Крутизна gate-функции |

`extra="allow"` — допускает дополнительные поля (например, `rating_set_id`).

### RatingPlayerRequest

Входные данные игрока для расчёта эффективного рейтинга.

| Field | Type | Description |
|-------|------|-------------|
| `member_id` | `UUID` | ID игрока |
| `role_id` | `UUID` | ID роли |
| `open_rating` | `float` | Открытый рейтинг |
| `priority` | `int` | Приоритет роли (0 = минимальный) |

### PlayerEffectiveRating

Ответ от расчёта эффективного рейтинга.

| Field | Type | Description |
|-------|------|-------------|
| `member_id` | `UUID` | ID игрока |
| `role_id` | `UUID` | ID роли |
| `open_rating` | `float` | Открытый рейтинг |
| `effective_rating` | `float` | Эффективный рейтинг |
| `hidden_rating` | `float` | Проецируемый скрытый рейтинг в открытую систему |

### MatchTeamInput

Данные команды для обработки результата матча.

| Field | Type | Description |
|-------|------|-------------|
| `team_id` | `UUID` | ID команды |
| `player_ids` | `list[UUID]` | ID игроков в команде |

### MatchPlayerInput

Данные игрока для обработки результата матча.

| Field | Type | Description |
|-------|------|-------------|
| `member_id` | `UUID` | ID игрока |
| `role_id` | `UUID` | ID роли |
| `open_rating` | `float` | Открытый рейтинг на момент матча |
