# TeamPlayer

- **ORM file:** `src/core/models/team_player.py`
- **Repo protocol:** `TeamPlayerRepositoryProtocol`
- **Used by services:** `TeamFormationService`, `MatchService`

## Role
Член команды. Связывает участника с командой, хранит игровую роль и рейтинг.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `team_id` | `UUID` | ID команды |
| `member_id` | `UUID` | ID участника |
| `game_role_id` | `UUID` | ID игровой роли в команде |
| `rating` | `float` | Рейтинг игрока (calculated rating из balancer) |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `team` | `Team \| None` | Родительская команда |
| `game_role` | `SelectedGameRole \| None` | Игровая роль |

## Create/Update Models

### Create — `TeamPlayerCreate` (`src/core/models/team_player.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `team_id` | `UUID` | Yes | — | FK, неизменяем |
| `member_id` | `UUID` | Yes | — | FK, неизменяем |
| `game_role_id` | `UUID` | Yes | — | FK |
| `rating` | `float` | Yes | — | |

### Update — `TeamPlayerUpdate` (`src/core/models/team_player.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `game_role_id` | `UUID \| None` | No | `None` | |
| `rating` | `float \| None` | No | `None` | |

> Поля `team_id` и `member_id` неизменяемы и не включены в Update-модель.

### Read — `TeamPlayer` (`src/core/models/team_player.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `team_id` | `UUID` | |
| `member_id` | `UUID` | |
| `game_role_id` | `UUID` | |
| `rating` | `float` | |
| `team` | `Team \| None` | Навигационное свойство |
| `game_role` | `SelectedGameRole \| None` | Навигационное свойство |
