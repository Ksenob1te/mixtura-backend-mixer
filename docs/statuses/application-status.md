# ApplicationStatus — Transitions

**Enum:** `src/core/models/application.py:17` | `ApplicationStatus(str, enum.Enum)`
**No formal state machine** — валидация только через сервисные guard-проверки

Статус заявки на участие в событии. Управляется через `ApplicationService.submit()` и `ApplicationService.review()`.

## States

| State | Description | Terminal |
|-------|-------------|----------|
| `PENDING` | Заявка на рассмотрении (если событие использует manual review) | No |
| `APPROVED` | Заявка одобрена — игрок добавлен в событие | No |
| `REJECTED` | Заявка отклонена — игрок удалён из события | Yes |
| `WAITLIST` | Заявка в листе ожидания | No |

## Transition Diagram

```
                    ┌─────────────┐
                    │             │
             ┌─────►│  PENDING    │◄──────┐
             │      │             │       │
             │      └──────┬──────┘       │
             │             │              │
             │             │ review()     │ review()
             │             │ (APPROVED)   │ (REJECTED)
             │             ▼              │
             │      ┌─────────────┐       │
             │      │             │       │
             │      │  APPROVED   │       │
             │      │             │       │
             │      └─────────────┘       │
             │                            │
             │      ┌─────────────┐       │
             │      │             │       │
             │      │  REJECTED   │◄──────┘
             │      │  (terminal) │
             │      └─────────────┘
             │
             │      ┌─────────────┐
             │      │             │
             └──────┤  WAITLIST   │
                    │             │
                    └─────────────┘
```

## Transition Triggers

### 1. Submit — `ApplicationService.submit()` (`application.py:69`)

| Target Status | Condition | File:Line |
|---------------|-----------|-----------|
| `APPROVED` | `event.use_application == False` (auto-approval) | `application.py:147` |
| `PENDING` | `event.use_application == True` (manual review) | `application.py:147` |

**Guards before creation:**
- Event must exist
- Event must not be `COMPLETED` or `CANCELLED`
- Caller must be authenticated (member_id required)
- Caller must be on the same server as the event
- Ban checks: `R_MIX_BAN` for SINGLE events, `R_TOURNAMENT_BAN` for TOURNAMENT events
- No duplicate application for same member+event
- Time window: must be between `start_time` and `end_time` (if configured)
- Custom fields: all required fields present, no duplicates, no unknown fields
- Required integrations: all present
- Role priorities: all valid, no duplicates

**Side effects:**
- Creates `Application`
- Creates `FilledApplicationField`s
- Creates `ApplicationIntegration`s
- Creates `EventPlayer` with status `REGISTERED`
- Creates `PlayerRole`s

### 2. Review — `ApplicationService.review()` (`application.py:194`)

**Common guards (all targets):**
- Application must exist
- Event must exist
- Caller: same server, organizer OR `P_EVENT_ADMIN_MANAGE_PLAYERS`
- Event must not be `COMPLETED` or `CANCELLED`

#### 2a. APPROVED (`application.py:222`)

| Action | Details |
|--------|---------|
| **Application status** | `ApplicationUpdate(status=APPROVED)` (line 232) |
| **EventPlayer** | If exists: update to `REGISTERED` (line 241). If not exists: create new `EventPlayer` with `REGISTERED` (line 244). |
| **Guard (EventPlayer)** | If existing player status is `PLAYING` → `ConflictException` (line 237) |
| **Roles** | If `command.role_priorities` provided: create new `PlayerRole`s for any not already existing |

#### 2b. REJECTED (`application.py:290`)

| Action | Details |
|--------|---------|
| **Application status** | `ApplicationUpdate(status=REJECTED)` (line 297) |
| **EventPlayer** | Deleted if exists (line 292) |
| **Result** | Returns `ApplicationReviewResult` with status `REJECTED`, no `player_id` |

#### 2c. WAITLIST (`application.py:302`)

| Action | Details |
|--------|---------|
| **Application status** | `ApplicationUpdate(status=WAITLIST)` (line 306) |
| **EventPlayer** | Not modified |

#### 2d. Unsupported status (`application.py:311`)

Any other `ApplicationStatus` value → `BadRequestException("Unsupported application status: {new_status}")`

## Services That Guard on ApplicationStatus

| Service | Method | Guard |
|---------|--------|-------|
| `ApplicationService` | `get_list()` | Accepts `status` filter parameter for querying |

## Default Status

- `ApplicationCreate.status` defaults to `PENDING` (`application.py:41`)
- Overridden in `submit()`: `APPROVED` if auto-approval, `PENDING` if manual
