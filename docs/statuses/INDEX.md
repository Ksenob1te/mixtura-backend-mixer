# Status Machines

В системе 4 статус-перечисления, каждое со своей логикой переходов. Только `EventStatus` имеет формальную машину состояний (декларативный конфиг + валидация в ORM). Остальные валидируются на уровне сервисных guard-проверок.

> См. также [_shared/enums.md](../_shared/enums.md) — краткое описание каждого enum.

## Status Machines

| Status | File | Source | Formal Validator | Documentation |
|--------|------|--------|------------------|---------------|
| `EventStatus` | `src/core/models/event.py:27` | `src/config/event_flow.ini` | `EventModel.transition_to()` in ORM | [event-status.md](event-status.md) |
| `EventPlayerStatus` | `src/core/models/event_player.py:16` | Service guards only | Нет | [event-player-status.md](event-player-status.md) |
| `ApplicationStatus` | `src/core/models/application.py:17` | Service guards only | Нет | [application-status.md](application-status.md) |
| `DraftStatus` | `src/core/models/draft.py:15` | Service guards only | Нет | [draft-status.md](draft-status.md) |

## Cross-Object Status Interactions

Статусы разных объектов взаимосвязаны через сервисные guard-проверки:

- **Event.status** блокирует мутации в Settings (CREATED/IDLE), Application (COMPLETED/CANCELLED), Player (CANCELLED/COMPLETED), Organizer (COMPLETED/CANCELLED), Match (CREATED/COMPLETED/CANCELLED), Draft (только REGISTRATION/IDLE/IN_PROGRESS)
- **EventPlayer.status** в `PLAYING` блокирует удаление и изменение статуса через `PlayerService` (но не через `MatchService.record_result`)
- **Draft.status** контролируется только через `TeamFormationService` (OPEN → BALANCE_REQUESTED → BALANCE_SELECTED)
- **Application → EventPlayer:** `review(APPROVED)` создаёт или активирует `EventPlayer`; `review(REJECTED)` удаляет `EventPlayer`
- **Match → EventPlayer:** `record_result()` переводит игроков из `PLAYING` в `REGISTERED` (в обход guard в `PlayerService`)

## Implementation Notes

- Все enum-ы — `str, enum.Enum`; сериализуются как строки
- `EventStatus` — единственный с формальной машиной состояний; нарушение перехода → `ValueError` → `ConflictException`
- У остальных статусов нет формальной валидации: `*Update` DTO принимают любое значение enum, guard-проверки только в сервисах
- Тесты репозиториев (`tests/repo/`) проверяют ORM-модели включая `transition_to()` для Event
- Тесты сервисов (`tests/services/`) проверяют guard-логику и переходы статусов
