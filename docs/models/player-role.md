# PlayerRole

- **ORM file:** `src/core/models/player_role.py`
- **Repo protocol:** `PlayerRoleRepositoryProtocol`
- **Used by services:** `ApplicationService`, `TeamFormationService`

## Role
Роль, выбранная игроком в событии. Связывает `EventPlayer` с `SelectedGameRole` и хранит приоритет предпочтения.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `game_role_id` | `UUID` | ID выбранной игровой роли (`SelectedGameRole.id`) |
| `priority` | `int` | Приоритет роли (меньше = предпочтительнее) |
| `event_player_id` | `UUID` | ID участника |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `game_role` | `SelectedGameRole \| None` | Игровая роль |
| `event_player` | `EventPlayer \| None` | Участник |

## Create/Update Models

### Create — `PlayerRoleCreate` (`src/core/models/player_role.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `game_role_id` | `UUID` | Yes | — | FK |
| `priority` | `int` | Yes | — | |
| `event_player_id` | `UUID` | Yes | — | FK, неизменяем |

### Update — `PlayerRoleUpdate` (`src/core/models/player_role.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `game_role_id` | `UUID \| None` | No | `None` | |
| `priority` | `int \| None` | No | `None` | |

> Поле `event_player_id` неизменяемо и не включено в Update-модель.

### Read — `PlayerRole` (`src/core/models/player_role.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `game_role_id` | `UUID` | |
| `priority` | `int` | |
| `event_player_id` | `UUID` | |
| `game_role` | `SelectedGameRole \| None` | Навигационное свойство |
| `event_player` | `EventPlayer \| None` | Навигационное свойство |
