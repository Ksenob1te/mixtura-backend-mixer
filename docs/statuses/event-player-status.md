# EventPlayerStatus — Transitions

**Enum:** `src/core/models/event_player.py:16` | `EventPlayerStatus(str, enum.Enum)`
**No formal state machine** — валидация только через сервисные guard-проверки

Статус игрока в событии. Отражает жизненный цикл от регистрации до завершения участия.

## States

| State | Description |
|-------|-------------|
| `REGISTERED` | Игрок зарегистрирован, доступен для draft |
| `SELECTED` | Игрок выбран в draft или в команду (через team formation) |
| `PLAYING` | Игрок участвует в активном матче |
| `COMPLETED` | Игрок завершил участие |
| `BENCHED` | Игрок на скамейке запасных, доступен для draft (при `allow_multiple_drafts`) |

## Transition Diagram

```
                   ┌─────────────┐
  submit() /       │             │     remove()
  review(APPROVE)  │ REGISTERED  │◄────────────────────┐
  ────────────────►│             │                      │
                   └──────┬──────┘                      │
                          │                             │
                          │ draft.create() /            │
                          │ formation.choose_variant()  │
                          │ (→ SELECTED)                │
                          ▼                             │
                   ┌─────────────┐                      │
                   │             │                      │
                   │  SELECTED   │                      │
                   │             │                      │
                   └──────┬──────┘                      │
                          │                             │
                          │ match.setup()               │
                          │ (implicit: team → slot)     │
                          ▼                             │
                   ┌─────────────┐                      │
                   │             │     match            │
                   │  PLAYING    │────.record_result()──┘
                   │             │     (→ REGISTERED)
                   └──────┬──────┘
                          │
                          │ player.update_status()
                          ▼
                   ┌─────────────┐
                   │             │
                   │  COMPLETED  │
                   │             │
                   └─────────────┘

  BENCHED: устанавливается через player.update_status(BENCHED)
           из REGISTERED; может быть drafted (→ SELECTED)
```

## Transition Triggers

| # | Transition | Trigger (Service Method) | Source File | Conditions / Guards |
|---|-----------|--------------------------|-------------|---------------------|
| 1 | *(new)* → `REGISTERED` | `ApplicationService.submit()` | `application.py:170` | Default for `EventPlayerCreate`. Always created when application submitted. |
| 1b | *(new)* → `REGISTERED` | `ApplicationService.review(APPROVED)` | `application.py:244` | Creates player if not exists; updates existing player to `REGISTERED` |
| 1c | *(new)* → `REGISTERED` | `PlayerService.add()` | `player.py:119` | Default for `EventPlayerCreate`. Guard: event not COMPLETED/CANCELLED. |
| 2 | `REGISTERED` / `BENCHED` → `SELECTED` | `DraftService.create()` | `draft.py:102` | Event status must be `REGISTRATION`/`IDLE`/`IN_PROGRESS`. If `!allow_multiple_drafts`: player must not be busy in active match draft. If `allow_multiple_drafts`: `SELECTED` players also allowed. |
| 2b | Any → `SELECTED` | `TeamFormationService.choose_variant()` | `team_formation.py:336` | Draft status must be `BALANCE_REQUESTED`/`OPEN`. Job must not be `"pending"`. Each variant player updated to `SELECTED`. |
| 3 | `SELECTED` → `PLAYING` | *(implicit via `MatchService.setup()`)* | — | When a team is placed in a match slot. No explicit status update — status must be set externally (e.g., via `PlayerService.update_status()`) |
| 4 | Any → Any | `PlayerService.update_status()` | `player.py:91` | **Guard:** event status must not be `CANCELLED`. **Guard:** if current status is `PLAYING`, can only transition to `PLAYING` (cannot leave). |
| 5 | `PLAYING` → `REGISTERED` | `MatchService.record_result()` | `match.py:197` | Bypasses `PlayerService.update_status()` guard (calls `player_repo.update()` directly). Match must not already be completed. Only for `SINGLE` match type with `SINGLE_MATCH` stage format. |

## Critical Guard: PLAYING Lock

В `PlayerService.update_status()` (`player.py:85-89`):

```python
if player.status == EventPlayerStatus.PLAYING:
    if command.status != EventPlayerStatus.PLAYING:
        raise BadRequestException("Cannot change status of a player currently in an active match")
```

Это предотвращает удаление/изменение статуса играющего игрока через обычные операции. Однако `MatchService.record_result()` **обходит** эту проверку, вызывая `player_repo.update()` напрямую с `EventPlayerStatus.REGISTERED`.

Аналогичная guard-проверка в `PlayerService.remove()` (`player.py:230-233`): нельзя удалить игрока со статусом `PLAYING`.

## Services That Guard on EventPlayerStatus

| Service | Method(s) | Guard | Condition |
|---------|-----------|-------|-----------|
| `PlayerService` | `update_status()` | Block transition away from `PLAYING` | `current == PLAYING and new != PLAYING` |
| `PlayerService` | `remove()` | Block removal of `PLAYING` player | `status == PLAYING` |
| `ApplicationService` | `review(APPROVED)` | Block if existing player is `PLAYING` | `existing_player.status == PLAYING` |
| `DraftService` | `create()` | Only draft players with allowed statuses | `p.status in (REGISTERED, BENCHED)` + `SELECTED` if `allow_multiple_drafts` |

## Default Status

- При создании через `EventPlayerCreate`: `REGISTERED` (default в доменной модели)
- При создании через `submit()` или `add()`: `REGISTERED` (через default модели)
