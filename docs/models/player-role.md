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
| `game_role_id` | `UUID` | ID выбранной игровой роли (`SelectedGameRole.id`), неизменяем |
| `priority` | `int` | Приоритет роли (больше = предпочтительнее, 0 = не играет этой ролью) |
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
| `priority` | `int \| None` | No | `None` | |

> Поля `id`, `game_role_id` и `event_player_id` неизменяемы и не включены в Update-модель.

### Read — `PlayerRole` (`src/core/models/player_role.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `game_role_id` | `UUID` | |
| `priority` | `int` | |
| `event_player_id` | `UUID` | |
| `game_role` | `SelectedGameRole \| None` | Навигационное свойство |
| `event_player` | `EventPlayer \| None` | Навигационное свойство |
