# SingleMatchView

- **Source:** `src/core/results/match.py`
- **Used by queues:** `event.match.setup`, `event.match.get`, `event.match.list`, `event.match.result.record`

## SingleMatchView

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `UUID` | ID события |
| `bracket_id` | `UUID` | ID bracket (для tournament) |
| `stage_id` | `UUID` | ID этапа (для tournament) |
| `group_id` | `UUID` | ID группы (для tournament) |
| `match_id` | `UUID` | ID матча |
| `match_index` | `int` | Номер матча |
| `draft_id` | `UUID \| None` | ID draft (если матч из draft) |
| `completed_at` | `datetime \| None` | Время завершения матча |
| `slots` | `list[SingleMatchSlotView]` | Слоты с командами и счётом |

## Nested Types

### SingleMatchSlotView

| Field | Type | Description |
|-------|------|-------------|
| `slot_id` | `UUID` | |
| `slot_num` | `int` | Номер слота |
| `team_id` | `UUID` | ID команды в слоте |
| `score_id` | `UUID` | ID записи счёта |
| `score` | `int` | Счёт команды |
