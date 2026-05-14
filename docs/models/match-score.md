# MatchScore

- **ORM file:** `src/core/models/match_score.py`
- **Repo protocol:** `MatchScoreRepositoryProtocol`
- **Used by services:** `MatchService`

## Role
Счёт команды в слоте матча. Создаётся при setup матча, обновляется при record_result.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `slot_id` | `UUID` | ID слота |
| `team_id` | `UUID` | ID команды |
| `score` | `int` | Счёт (неотрицательное целое) |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `slot` | `MatchSlot \| None` | Родительский слот |
| `team` | `Team \| None` | Команда |

## Create/Update Models

### Create — `MatchScoreCreate` (`src/core/models/match_score.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `slot_id` | `UUID` | Yes | — | FK, неизменяем |
| `team_id` | `UUID` | Yes | — | FK, неизменяем |
| `score` | `int` | Yes | — | Обычно инициализируется как 0 |

### Update — `MatchScoreUpdate` (`src/core/models/match_score.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `score` | `int \| None` | No | `None` | |

> Поля `slot_id` и `team_id` неизменяемы и не включены в Update-модель.

### Read — `MatchScore` (`src/core/models/match_score.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `slot_id` | `UUID` | |
| `team_id` | `UUID` | |
| `score` | `int` | |
| `slot` | `MatchSlot \| None` | Навигационное свойство |
| `team` | `Team \| None` | Навигационное свойство |
