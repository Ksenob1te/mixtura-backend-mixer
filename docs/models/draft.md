# Draft

- **ORM file:** `src/core/models/draft.py`
- **Repo protocol:** `DraftRepositoryProtocol`
- **Used by services:** `DraftService`, `TeamFormationService`, `MatchService`

## Role
Draft-сессия — набор игроков, доступных для выбора в команды. Проходит через статусы `OPEN` → `BALANCE_REQUESTED` → `BALANCE_SELECTED` → `COMPLETED`.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `status` | `DraftStatus` | Текущий статус draft-сессии |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `teams` | `list[Team]` | Команды, созданные из этого draft |
| `drafted_players` | `list[DraftedPlayer]` | Игроки в draft |

## Create/Update Models

### Create — `DraftCreate` (`src/core/models/draft.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `status` | `DraftStatus` | No | `DraftStatus.OPEN` | |

### Update — `DraftUpdate` (`src/core/models/draft.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `status` | `DraftStatus \| None` | No | `None` | |

> Поля `id` и `event_id` неизменяемы и не включены в Update-модель.

### Read — `Draft` (`src/core/models/draft.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `status` | `DraftStatus` | |
| `event` | `Event \| None` | Навигационное свойство |
| `teams` | `list[Team]` | Навигационное свойство |
| `drafted_players` | `list[DraftedPlayer]` | Навигационное свойство |
