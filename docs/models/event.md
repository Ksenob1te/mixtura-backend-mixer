# Event

- **ORM file:** `src/core/models/event.py`
- **Repo protocol:** `EventRepositoryProtocol`
- **Used by services:** `EventService`, `ApplicationService`, `OrganizerService`, `PlayerService`, `DraftService`, `TeamService`, `TeamFormationService`, `MatchService`, `SettingsService`

## Role
Центральная сущность системы. Представляет игровое событие с настройками формата, команд, регистрации и интеграций. Содержит связи со всеми дочерними сущностями.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор события |
| `name` | `str` | Название события |
| `match_type` | `EventMatchType` | Тип матча: `SINGLE` или `TOURNAMENT` |
| `use_application` | `bool` | Требуется ли заявка для участия |
| `is_public` | `bool` | Видимо ли событие для всех пользователей сервера |
| `team_size` | `int` | Размер команды (количество игроков) |
| `team_formation` | `TeamFormation` | Метод формирования: `DRAFT`, `BALANCE`, `MANUAL` |
| `status` | `EventStatus` | Текущий статус жизненного цикла |
| `allow_multiple_drafts` | `bool` | Разрешены ли параллельные draft-сессии |
| `rating_set_id` | `UUID \| None` | ID набора рейтингов для effective rating |
| `server_id` | `UUID` | ID сервера-владельца |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `applications` | `list[Application]` | Заявки на участие |
| `teams` | `list[Team]` | Команды события |
| `drafts` | `list[Draft]` | Draft-сессии |
| `organizers` | `list[Organizer]` | Организаторы |
| `event_players` | `list[EventPlayer]` | Участники |
| `brackets` | `list[Bracket]` | Турнирные сетки |
| `required_integrations` | `list[RequiredIntegration]` | Обязательные интеграции |
| `selected_game_roles` | `list[SelectedGameRole]` | Выбранные игровые роли |
| `custom_fields` | `list[ApplicationCustomField]` | Кастомные поля заявки |
| `time_settings` | `ApplicationTimeSettings \| None` | Временные окна регистрации |

## Create/Update Models

### Create — `EventCreate` (`src/core/models/event.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str` | Yes | — | |
| `match_type` | `EventMatchType` | Yes | — | |
| `use_application` | `bool` | Yes | — | |
| `is_public` | `bool` | Yes | — | |
| `team_size` | `int` | Yes | — | |
| `team_formation` | `TeamFormation` | Yes | — | |
| `allow_multiple_drafts` | `bool` | Yes | — | |
| `status` | `EventStatus` | No | `EventStatus.CREATED` | |
| `rating_set_id` | `UUID \| None` | No | `None` | |
| `server_id` | `UUID` | Yes | — | |

### Update — `EventUpdate` (`src/core/models/event.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str \| None` | No | `None` | |
| `match_type` | `EventMatchType \| None` | No | `None` | |
| `use_application` | `bool \| None` | No | `None` | |
| `is_public` | `bool \| None` | No | `None` | |
| `team_size` | `int \| None` | No | `None` | |
| `team_formation` | `TeamFormation \| None` | No | `None` | |
| `allow_multiple_drafts` | `bool \| None` | No | `None` | |
| `rating_set_id` | `UUID \| None` | No | `None` | |

> Поля `id` и `server_id` неизменяемы и не включены в Update-модель.

### Read — `Event` (`src/core/models/event.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `name` | `str` | |
| `match_type` | `EventMatchType` | |
| `use_application` | `bool` | |
| `is_public` | `bool` | |
| `team_size` | `int` | |
| `team_formation` | `TeamFormation` | |
| `status` | `EventStatus` | |
| `allow_multiple_drafts` | `bool` | |
| `rating_set_id` | `UUID \| None` | |
| `server_id` | `UUID` | |
| `applications` | `list[Application]` | Навигационное свойство |
| `teams` | `list[Team]` | Навигационное свойство |
| `drafts` | `list[Draft]` | Навигационное свойство |
| `organizers` | `list[Organizer]` | Навигационное свойство |
| `event_players` | `list[EventPlayer]` | Навигационное свойство |
| `brackets` | `list[Bracket]` | Навигационное свойство |
| `required_integrations` | `list[RequiredIntegration]` | Навигационное свойство |
| `selected_game_roles` | `list[SelectedGameRole]` | Навигационное свойство |
| `custom_fields` | `list[ApplicationCustomField]` | Навигационное свойство |
| `time_settings` | `ApplicationTimeSettings \| None` | Навигационное свойство |
