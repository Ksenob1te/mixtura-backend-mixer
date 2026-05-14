# SelectedGameRole

- **ORM file:** `src/core/models/selected_game_role.py`
- **Repo protocol:** `SelectedGameRoleRepositoryProtocol`
- **Used by services:** `SettingsService`, `ApplicationService`, `TeamFormationService`

## Role
Игровая роль, выбранная для события. Связывает глобальную `game_role_id` с событием и задаёт ограничения на количество игроков с этой ролью в команде.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `game_role_id` | `UUID` | Глобальный ID игровой роли (из внешнего сервиса) |
| `event_id` | `UUID` | ID события |
| `override_max_count` | `int \| None` | Макс. количество игроков с этой ролью в команде |
| `override_min_count` | `int \| None` | Мин. количество игроков с этой ролью в команде |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `player_roles` | `list[PlayerRole]` | Выборы ролей игроками |
| `team_players` | `list[TeamPlayer]` | Назначения ролей в командах |

## Create/Update Models

### Create — `SelectedGameRoleCreate` (`src/core/models/selected_game_role.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `game_role_id` | `UUID` | Yes | — | |
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `override_max_count` | `int \| None` | No | `None` | |
| `override_min_count` | `int \| None` | No | `None` | |

### Update — `SelectedGameRoleUpdate` (`src/core/models/selected_game_role.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `override_max_count` | `int \| None` | No | `None` | |
| `override_min_count` | `int \| None` | No | `None` | |

> Поля `id`, `game_role_id` и `event_id` неизменяемы и не включены в Update-модель.

### Read — `SelectedGameRole` (`src/core/models/selected_game_role.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `game_role_id` | `UUID` | |
| `event_id` | `UUID` | |
| `override_max_count` | `int \| None` | |
| `override_min_count` | `int \| None` | |
| `event` | `Event \| None` | Навигационное свойство |
| `player_roles` | `list[PlayerRole]` | Навигационное свойство |
| `team_players` | `list[TeamPlayer]` | Навигационное свойство |
