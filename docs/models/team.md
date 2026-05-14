# Team

- **ORM file:** `src/core/models/team.py`
- **Repo protocol:** `TeamRepositoryProtocol`
- **Used by services:** `TeamService`, `TeamFormationService`, `MatchService`

## Role
Команда в событии. Создаётся автоматически при формировании команд (`BALANCE`) или вручную. Содержит игроков.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `draft_id` | `UUID \| None` | ID draft-сессии (если создана из draft) |
| `name` | `str` | Название команды |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `draft` | `Draft \| None` | Связанная draft-сессия |
| `players` | `list[TeamPlayer]` | Члены команды |

## Create/Update Models

### Create — `TeamCreate` (`src/core/models/team.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `draft_id` | `UUID \| None` | No | `None` | FK, неизменяем |
| `name` | `str` | Yes | — | |

### Update — `TeamUpdate` (`src/core/models/team.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str \| None` | No | `None` | |

> Поля `id`, `event_id` и `draft_id` неизменяемы и не включены в Update-модель.

### Read — `Team` (`src/core/models/team.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `draft_id` | `UUID \| None` | |
| `name` | `str` | |
| `event` | `Event \| None` | Навигационное свойство |
| `draft` | `Draft \| None` | Навигационное свойство |
| `players` | `list[TeamPlayer]` | Навигационное свойство |
