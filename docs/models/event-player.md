# EventPlayer

- **ORM file:** `src/core/models/event_player.py`
- **Repo protocol:** `PlayerRepositoryProtocol`
- **Used by services:** `ApplicationService`, `PlayerService`, `DraftService`, `TeamFormationService`, `MatchService`

## Role
Участник события (игрок). Связывает member с event, хранит статус участия и выбранные роли.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `member_id` | `UUID` | ID участника (глобальный) |
| `application_id` | `UUID \| None` | Связанная заявка (если была) |
| `custom_id` | `UUID \| None` | ID оценки игрока (рейтинги на разных ролях). Организатор может менять оценку, поле обновляемое |
| `is_draft_pinned` | `bool` | Закреплён ли для draft (приоритетный игрок) |
| `status` | `EventPlayerStatus` | Текущий статус участия |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `application` | `Application \| None` | Связанная заявка |
| `drafted_players` | `list[DraftedPlayer]` | Вхождения в draft-сессии |
| `player_roles` | `list[PlayerRole]` | Выбранные роли с приоритетами |

## Enums

### EventPlayerStatus

| Value | Description |
|-------|-------------|
| `REGISTERED` | Игрок зарегистрирован, ожидает формирования команд |
| `SELECTED` | Игрок выбран в команду (draft/balance/manual) |
| `PLAYING` | Игрок участвует в активном матче |
| `COMPLETED` | Игрок завершил участие в событии |
| `BENCHED` | Игрок на скамейке (не участвует в текущем матче) |

## Create/Update Models

### Create — `EventPlayerCreate` (`src/core/models/event_player.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `member_id` | `UUID` | Yes | — | FK, неизменяем |
| `application_id` | `UUID \| None` | No | `None` | FK |
| `custom_id` | `UUID \| None` | No | `None` | |
| `is_draft_pinned` | `bool` | No | `False` | |

### Update — `EventPlayerUpdate` (`src/core/models/event_player.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `is_draft_pinned` | `bool \| None` | No | `None` | |
| `status` | `EventPlayerStatus \| None` | No | `None` | |
| `custom_id` | `UUID \| None` | No | `None` | ID оценки игрока, обновляемый |

> Поля `id`, `event_id`, `member_id` и `application_id` неизменяемы и не включены в Update-модель.

### Read — `EventPlayer` (`src/core/models/event_player.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `member_id` | `UUID` | |
| `application_id` | `UUID \| None` | |
| `custom_id` | `UUID \| None` | |
| `is_draft_pinned` | `bool` | |
| `status` | `EventPlayerStatus` | |
| `event` | `Event \| None` | Навигационное свойство |
| `application` | `Application \| None` | Навигационное свойство |
| `drafted_players` | `list[DraftedPlayer]` | Навигационное свойство |
| `player_roles` | `list[PlayerRole]` | Навигационное свойство |
