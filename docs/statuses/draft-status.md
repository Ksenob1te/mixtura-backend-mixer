# DraftStatus — Transitions

**Enum:** `src/core/models/draft.py:15` | `DraftStatus(str, enum.Enum)`
**No formal state machine** — валидация только через сервисные guard-проверки в `TeamFormationService`

Статус draft-сессии. Отражает прогресс от создания до завершения (через выбор состава команд вручную или через балансировщик).

## States

| State | Description | Terminal |
|-------|-------------|----------|
| `OPEN` | Draft открыт, игроки могут быть выбраны | No |
| `BALANCE_REQUESTED` | Запрошен балансировщик, варианты генерируются асинхронно | No |
| `BALANCE_SELECTED` | Вариант балансировки выбран, команды созданы | No |
| `COMPLETED` | Draft завершён (ручной выбор завершён) | Yes |

## Transition Diagram

```
  ┌─────────────┐
  │             │
  │    OPEN     │◄────────────────────────────┐
  │             │                             │
  └──────┬──────┘                             │
         │                                    │
         │ formation.run()                    │
         │ (→ BALANCE_REQUESTED)              │
         ▼                                    │
  ┌──────────────────────┐                    │
  │                      │                    │
  │  BALANCE_REQUESTED   │                    │
  │                      │                    │
  └──────────┬───────────┘                    │
             │                                │
             │ formation.choose_variant()     │
             │ (→ BALANCE_SELECTED)           │
             ▼                                │
  ┌──────────────────────┐                    │
  │                      │                    │
  │  BALANCE_SELECTED    │                    │
  │                      │                    │
  └──────────────────────┘                    │
                                              │
  ┌──────────────────────┐                    │
  │                      │                    │
  │      COMPLETED       │ (ручной переход    │
  │      (terminal)      │  вне documented    │
  │                      │  flow)             │
  └──────────────────────┘                    │
```

## Transition Triggers

### 1. *(new)* → `OPEN` — `DraftService.create()` (`draft.py:96`)

Default status from `DraftCreate` model.

**Guards:**
- Event status must be `REGISTRATION`, `IDLE`, or `IN_PROGRESS`
- Caller: organizer OR `P_EVENT_ADMIN_MANAGE_PLAYERS`
- Players must have allowed statuses: `REGISTERED`, `BENCHED` (+ `SELECTED` if `allow_multiple_drafts`)
- If `!allow_multiple_drafts`: players in active match drafts are excluded
- At least one eligible player must exist

**Side effects:**
- Creates `DraftedPlayer` records
- Updates each drafted player's status to `EventPlayerStatus.SELECTED`

### 2. `OPEN` → `BALANCE_REQUESTED` — `TeamFormationService.run()` (`team_formation.py:175`)

**Guards:**
- Draft must be in `DraftStatus.OPEN` (line 112-113)
- Event `team_formation` must be `TeamFormationMethod.BALANCE` (line 115-116)
- Caller: organizer OR `P_EVENT_ADMIN_MANAGE_BRACKET`

**Side effects:**
- Builds rating snapshot for drafted players
- Saves `BalancerTask` in Redis with `status="pending"`
- Saves `TeamFormationJob` in Redis with `status="pending"`, TTL from `env.team_formation_variants_ttl_seconds`
- Publishes balancer request via RabbitMQ (mix or tournament depending on event `match_type`)

**Update:** `DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_REQUESTED)`

### 3. `BALANCE_REQUESTED` / `OPEN` → `BALANCE_SELECTED` — `TeamFormationService.choose_variant()` (`team_formation.py:341`)

**Guards:**
- Draft status must be `BALANCE_REQUESTED` or `OPEN` (line 294-295)
- Job status must NOT be `"pending"` (line 301-302) — "Team formation is still in progress"
- Variant must exist in cached job
- Variant must have at least one team

**Side effects:**
- Creates `Team` records for each variant team
- Creates `TeamPlayer` records with `game_role_id` and `calculated_rating`
- Updates each variant player's status to `EventPlayerStatus.SELECTED` (line 336)
- Deletes the cached variant job from Redis

**Update:** `DraftUpdate(id=cmd.draft_id, status=DraftStatus.BALANCE_SELECTED)`

### 4. Asynchronous Job Completion — `TeamFormationService.complete_formation()` (`team_formation.py:179`)

This is an **internal callback** from the balancer response handler, not triggered by a user command.

**No `DraftStatus` change** — only updates the Redis job:
- Retrieves `BalancerTask` from Redis
- Parses raw variants from balancer response
- Saves `TeamFormationJob` with `status="completed"` and populated variants
- Deletes `BalancerTask`

## Notes

- `DraftUpdate` может установить любое `DraftStatus` значение — нет формальной валидации переходов. Порядок гарантируется только сервисной логикой.
- `COMPLETED` статус не имеет документированного триггера в текущем коде (может быть ручным переходом или будущей функциональностью).
- `BALANCE_SELECTED` и `OPEN` оба допустимы для `choose_variant()` — это позволяет выбрать вариант даже если `run()` не был вызван (если job уже в кеше).
- Статусы в Redis (`BalancerTask.status`, `TeamFormationJob.status`) не являются enum-ами, а простыми строками `"pending"` / `"completed"`.
