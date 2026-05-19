# EventStatus — State Machine

**Enum:** `src/core/models/event.py:27` | `EventStatus(str, enum.Enum)`
**Transition config:** `src/config/event_flow.ini`
**Validation:** `EventModel.transition_to()` — `src/infra/postgre/models/event.py:82`
**Repository:** `EventRepository.transition_status()` — `src/infra/postgre/repo/event.py:108`

Единственный статус с формальной машиной состояний. Переходы декларированы в `event_flow.ini` и проверяются в ORM-модели перед сохранением.

## States

| State | Description | Terminal |
|-------|-------------|----------|
| `CREATED` | Событие создано, настройки не завершены | No |
| `REGISTRATION` | Регистрация открыта, принимаются заявки | No |
| `IDLE` | Регистрация закрыта, ожидание дальнейших действий | No |
| `FORMATION` | Формирование команд (автоматически при балансировке) | No |
| `IN_PROGRESS` | Матчи в процессе | No |
| `COMPLETED` | Событие завершено | Yes |
| `CANCELLED` | Событие отменено | Yes |

## Allowed Transitions (from `event_flow.ini`)

```
                    ┌─────────────┐
                    │             │
          ┌─────────┤   CREATED   ├─────────┐
          │         │             │         │
          ▼         └──────┬──────┘         │
   ┌──────────┐            │                │
   │          │            ▼                │
   │  IDLE    │◄───┌──────────────┐         │
   │          │    │              │         │
   └────┬─────┘    │ REGISTRATION │         │
        │          │              │         │
        │          └──────┬───────┘         │
        │                 │                 │
        │                 ▼                 │
        │          ┌──────────────┐         │
        │          │              │         │
        ├──────────┤  FORMATION   │         │
        │          │              │         │
        │          └──────┬───────┘         │
        │                 │                 │
        │                 ▼                 │
        │          ┌──────────────┐         │
        │          │              │         │
        ├──────────┤ IN_PROGRESS  │         │
        │          │              │         │
        │          └──────┬───────┘         │
        │                 │                 │
        ▼                 ▼                 ▼
 ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
 │              │  │              │  │              │
 │  COMPLETED   │  │  CANCELLED   │  │  CANCELLED   │
 │  (terminal)  │  │  (terminal)  │  │  (terminal)  │
 └──────────────┘  └──────────────┘  └──────────────┘
```

### Transition Map

| From | To |
|------|----|
| `CREATED` | `IDLE`, `REGISTRATION`, `COMPLETED`, `CANCELLED` |
| `REGISTRATION` | `IDLE`, `COMPLETED`, `FORMATION`, `CANCELLED` |
| `IDLE` | `FORMATION`, `COMPLETED`, `REGISTRATION`, `CANCELLED` |
| `FORMATION` | `IDLE`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| `IN_PROGRESS` | `IDLE`, `COMPLETED`, `CANCELLED` |
| `COMPLETED` | *(terminal — no further transitions)* |
| `CANCELLED` | *(terminal — no further transitions)* |

## Transition Triggers

| # | Transition | Trigger (Service Method) | Command | Permission Required | Additional Guards |
|---|-----------|--------------------------|---------|--------------------|--------------------|
| 1 | `CREATED` → `IDLE` | `EventService.activate()` (`event.py:200`) | `ActivateEventCommand` | Organizer OR `P_EVENT_ADMIN_UPDATE` | — |
| 2 | `CREATED` / `IDLE` → `REGISTRATION` | `EventService.open_registration()` (`event.py:226`) | `OpenRegistrationCommand` | Organizer OR `P_EVENT_ADMIN_UPDATE` | — |
| 3 | `REGISTRATION` / `FORMATION` / `IN_PROGRESS` → `IDLE` | `EventService.close_registration()` (`event.py:252`) | `CloseRegistrationCommand` | Organizer OR `P_EVENT_ADMIN_UPDATE` | — |
| 4 | Any non-terminal → `CANCELLED` | `EventService.cancel()` (`event.py:278`) | `CancelEventCommand` | Organizer OR `P_EVENT_ADMIN_CANCEL` | — |
| 5 | Any non-terminal → `COMPLETED` | `EventService.complete()` (`event.py:304`) | `CompleteEventCommand` | Organizer OR `P_EVENT_ADMIN_COMPLETE` | `match_type == SINGLE`; status not already `COMPLETED`/`CANCELLED`; no active matches |

## Services That Guard on EventStatus (Read-Only, No Transition)

| Service | Method(s) | Guarded States | Block Condition | Error Message |
|---------|-----------|----------------|-----------------|---------------|
| `EventService` | `update()` | `CREATED`, `IDLE` only | `status not in (CREATED, IDLE)` | "Event can only be updated before registration opens" |
| `SettingsService` | `add_integration`, `remove_integration`, `add_game_role`, `update_game_role`, `remove_game_role`, `add_custom_field`, `update_custom_field`, `remove_custom_field`, `update_time_settings` | `CREATED`, `IDLE` only | `status not in (CREATED, IDLE)` | "Cannot modify settings after registration opens" |
| `SettingsService` | `get_application_form_settings()` | Non-organizer: only `REGISTRATION` | `status != REGISTRATION` | "Registration not open yet" / "Registration is closed" |
| `ApplicationService` | `submit()` | `COMPLETED`, `CANCELLED` blocked | `status in (COMPLETED, CANCELLED)` | "Event is not accepting applications" |
| `ApplicationService` | `review()` | `COMPLETED`, `CANCELLED` blocked | `status in (COMPLETED, CANCELLED)` | "Cannot review applications for completed or cancelled event" |
| `PlayerService` | `add()` | `COMPLETED`, `CANCELLED` blocked | `status in (COMPLETED, CANCELLED)` | "Cannot add players to a completed or cancelled event" |
| `PlayerService` | `update_status()` | `CANCELLED` blocked | `status == CANCELLED` | "Cannot modify players in a cancelled event" |
| `PlayerService` | `update_roles()` | `COMPLETED`, `CANCELLED` blocked | `status in (COMPLETED, CANCELLED)` | "Cannot update player roles in a completed or cancelled event" |
| `PlayerService` | `remove()` | `CANCELLED` blocked | `status == CANCELLED` | "Cannot remove players from a cancelled event" |
| `OrganizerService` | `add()`, `remove()` | `COMPLETED`, `CANCELLED` blocked | `status == COMPLETED or status == CANCELLED` | "Cannot modify organizers of completed or cancelled event" |
| `MatchService` | `setup()` | `CREATED`, `COMPLETED`, `CANCELLED` blocked | `status in (CREATED, COMPLETED, CANCELLED)` | "Event status ... does not allow match setup" |
| `DraftService` | `create()` | `REGISTRATION`, `IDLE`, `IN_PROGRESS` only | `status not in (REGISTRATION, IDLE, IN_PROGRESS)` | "Event is not in a state that allows draft creation" |

## Validation Implementation

1. Конфиг загружается `EventFlowConfig.load_from_ini()` в `src/env_config.py:48`
2. При импорте `EventModel` строится `EVENT_STATUS_TRANSITIONS` (дикт `{EventStatus: set[EventStatus]}`)
3. `EventModel.transition_to(new_status)` вызывает `_validate_transition()` — проверяет, что `new_status` есть в `EVENT_STATUS_TRANSITIONS[self.status]`
4. При нарушении: `ValueError` → в репозитории конвертируется в `ConflictException`
5. Сервисные guard-проверки выполняются **до** вызова `transition_status()`
