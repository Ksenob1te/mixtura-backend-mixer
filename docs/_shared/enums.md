# Enums

Все enum-ы определены как `str, enum.Enum` и сериализуются в строковые значения.

## EventMatchType
- **File:** `src/core/models/event.py`
- **Используется:** Event, EventCreate, EventUpdate, EventCard, EventDetail

| Value | Description |
|-------|-------------|
| `SINGLE` | Одиночная игра (один матч между командами) |
| `TOURNAMENT` | Турнир с bracket/stages |

## EventStatus
- **File:** `src/core/models/event.py`
- **Используется:** Event, EventCard, EventDetail
- **Подробно:** [statuses/event-status.md](../statuses/event-status.md) — полная машина состояний, триггеры, guard-проверки

| Value | Description |
|-------|-------------|
| `CREATED` | Событие создано, настройки не завершены |
| `REGISTRATION` | Регистрация открыта (applications принимаются) |
| `IDLE` | Регистрация закрыта, ожидание начала |
| `FORMATION` | Формирование команд (автоматически при балансировке) |
| `IN_PROGRESS` | Событие в процессе (матчи идут) |
| `COMPLETED` | Событие завершено (терминальный) |
| `CANCELLED` | Событие отменено (терминальный) |

## TeamFormation
- **File:** `src/core/models/event.py`
- **Используется:** Event, EventCreate, EventUpdate

| Value | Description |
|-------|-------------|
| `DRAFT` | Капитаны выбирают игроков через draft |
| `BALANCE` | Автоматический балансировщик (mix/tournament balancer) |
| `MANUAL` | Ручное формирование команд |

## ApplicationStatus
- **File:** `src/core/models/application.py`
- **Используется:** Application, ApplicationCreate, ApplicationUpdate, SubmitApplicationCommand, ReviewApplicationCommand
- **Подробно:** [statuses/application-status.md](../statuses/application-status.md) — диаграмма переходов, триггеры, side effects

| Value | Description |
|-------|-------------|
| `PENDING` | Заявка на рассмотрении |
| `APPROVED` | Заявка одобрена |
| `REJECTED` | Заявка отклонена (терминальный) |
| `WAITLIST` | Заявка в листе ожидания |

## EventPlayerStatus
- **File:** `src/core/models/event_player.py`
- **Используется:** EventPlayer, EventPlayerUpdate, ListPlayersCommand, UpdatePlayerStatusCommand
- **Подробно:** [statuses/event-player-status.md](../statuses/event-player-status.md) — жизненный цикл, PLAYING lock, обход guard в MatchService

| Value | Description |
|-------|-------------|
| `REGISTERED` | Игрок зарегистрирован, доступен для draft |
| `SELECTED` | Игрок выбран в draft или в команду |
| `PLAYING` | Игрок участвует в активном матче |
| `COMPLETED` | Игрок завершил участие |
| `BENCHED` | Игрок на скамейке, доступен для draft (при allow_multiple_drafts) |

## DraftStatus
- **File:** `src/core/models/draft.py`
- **Используется:** Draft, DraftCreate, DraftUpdate
- **Подробно:** [statuses/draft-status.md](../statuses/draft-status.md) — переходы через балансировщик, асинхронный callback

| Value | Description |
|-------|-------------|
| `OPEN` | Draft открыт, игроки могут быть выбраны |
| `BALANCE_REQUESTED` | Запрошен балансировщик, варианты генерируются |
| `BALANCE_SELECTED` | Вариант выбран, команды созданы |
| `COMPLETED` | Draft завершён (терминальный) |

## StageFormat
- **File:** `src/core/models/stage.py`
- **Используется:** Stage, StageCreate, StageUpdate

| Value | Description |
|-------|-------------|
| `SINGLE_MATCH` | Одиночный матч (для single-game events) |
| `SINGLE_ELIMINATION` | Одиночная олимпийка |
| `DOUBLE_ELIMINATION` | Двойная олимпийка |
| `ROUND_ROBIN` | Каждый с каждым |
| `SWISS` | Швейцарская система |

## MatchSlotSourceType
- **File:** `src/core/models/match_slot.py`
- **Используется:** MatchSlot, MatchSlotCreate

| Value | Description |
|-------|-------------|
| `WINNER_OF` | Победитель указанного матча |
| `LOSER_OF` | Проигравший указанного матча |
| `GROUP_PLACEMENT` | Команда по месту в группе |
| `MANUAL` | Ручное назначение (single match setup) |
| `AUTO` | Автоматическое назначение |

## BracketPosition
- **File:** `src/core/models/match.py`
- **Используется:** Match, MatchCreate, MatchUpdate

| Value | Description |
|-------|-------------|
| `UPPER` | Верхняя сетка (double elimination) |
| `LOWER` | Нижняя сетка (double elimination) |
