# Match

- **ORM file:** `src/core/models/match.py`
- **Repo protocol:** `MatchRepositoryProtocol`
- **Used by services:** `MatchService`, `EventService`

## Role
Матч — единица игровой сессии. Может быть одиночным (`SINGLE_MATCH`) или частью турнира. Содержит слоты для команд и результат.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `group_id` | `UUID \| None` | ID группы этапа (для турниров) |
| `match_index` | `int \| None` | Порядковый номер матча в группе |
| `scheduled_at` | `datetime \| None` | Запланированное время начала |
| `time_start` | `datetime \| None` | Фактическое время начала |
| `time_end` | `datetime \| None` | Фактическое время окончания (не null = матч завершён) |
| `round_number` | `int \| None` | Номер раунда |
| `bracket_position` | `BracketPosition \| None` | Позиция в bracket (`UPPER`/`LOWER`) |
| `result_snapshot` | `dict \| None` | Снимок результата: scores, winner, forfeits, rating payload |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `group` | `StageGroup \| None` | Родительская группа |
| `slots` | `list[MatchSlot]` | Слоты матча (команды-участники) |
| `source_slots` | `list[MatchSlot]` | Слоты, где этот матч является источником |

## Create/Update Models

### Create — `MatchCreate` (`src/core/models/match.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `group_id` | `UUID \| None` | No | `None` | FK, неизменяем |
| `match_index` | `int \| None` | No | `None` | |
| `scheduled_at` | `datetime \| None` | No | `None` | |
| `time_start` | `datetime \| None` | No | `None` | |
| `time_end` | `datetime \| None` | No | `None` | |
| `round_number` | `int \| None` | No | `None` | |
| `bracket_position` | `BracketPosition \| None` | No | `None` | |
| `result_snapshot` | `dict \| None` | No | `None` | |

### Update — `MatchUpdate` (`src/core/models/match.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `scheduled_at` | `datetime \| None` | No | `None` | |
| `time_start` | `datetime \| None` | No | `None` | |
| `time_end` | `datetime \| None` | No | `None` | |
| `round_number` | `int \| None` | No | `None` | |
| `bracket_position` | `BracketPosition \| None` | No | `None` | |
| `result_snapshot` | `dict \| None` | No | `None` | |

> Поле `group_id` неизменяемо и не включено в Update-модель.

### Read — `Match` (`src/core/models/match.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `group_id` | `UUID \| None` | |
| `match_index` | `int \| None` | |
| `scheduled_at` | `datetime \| None` | |
| `time_start` | `datetime \| None` | |
| `time_end` | `datetime \| None` | |
| `round_number` | `int \| None` | |
| `bracket_position` | `BracketPosition \| None` | |
| `result_snapshot` | `dict \| None` | |
| `group` | `StageGroup \| None` | Навигационное свойство |
| `slots` | `list[MatchSlot]` | Навигационное свойство |
| `source_slots` | `list[MatchSlot]` | Навигационное свойство |
