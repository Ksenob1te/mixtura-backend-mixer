# DraftedPlayer

- **ORM file:** `src/core/models/drafted_player.py`
- **Repo protocol:** `DraftedPlayerRepositoryProtocol`
- **Used by services:** `DraftService`, `TeamFormationService`

## Role
Связь между draft-сессией и участником события. Определяет, какие игроки доступны для выбора в данном draft.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `draft_id` | `UUID` | ID draft-сессии |
| `event_player_id` | `UUID` | ID участника события |
| `is_captain` | `bool \| None` | Является ли капитаном (резерв для captain draft) |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `draft` | `Draft \| None` | Родительская draft-сессия |
| `event_player` | `EventPlayer \| None` | Участник |

## Create/Update Models

### Create — `DraftedPlayerCreate` (`src/core/models/drafted_player.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `draft_id` | `UUID` | Yes | — | FK, неизменяем |
| `event_player_id` | `UUID` | Yes | — | FK, неизменяем |
| `is_captain` | `bool \| None` | No | `None` | |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `DraftedPlayer` (`src/core/models/drafted_player.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `draft_id` | `UUID` | |
| `event_player_id` | `UUID` | |
| `is_captain` | `bool \| None` | |
| `draft` | `Draft \| None` | Навигационное свойство |
| `event_player` | `EventPlayer \| None` | Навигационное свойство |
