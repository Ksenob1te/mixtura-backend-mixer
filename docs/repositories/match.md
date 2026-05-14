# MatchRepository

**Protocol:** `src/core/interfaces/repo/match.py`
**Implementation:** `src/infra/postgre/repo/match.py`
**Model:** `Match` ([models/match.md](../models/match.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Match \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Match]` | |
| `create` | `(dto: MatchCreate) -> Match` | |
| `update` | `(match_id: UUID, dto: MatchUpdate) -> Match` | Takes `match_id` separately |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_slots: bool = False,
    load_group: bool = False,
) -> Match | None
```

### `list_by_stage_group`

```python
async def list_by_stage_group(group_id: UUID, offset: int, limit: int) -> Sequence[Match]
```

Lists matches for a stage group with pagination.

### `next_match_index`

```python
async def next_match_index(group_id: UUID) -> int
```

Returns the next available `match_index` for a stage group.

### `list_active_team_ids_by_event`

```python
async def list_active_team_ids_by_event(event_id: UUID) -> set[UUID]
```

Returns set of team IDs that have active (incomplete) matches in the event.

### `list_active_draft_ids_by_event`

```python
async def list_active_draft_ids_by_event(event_id: UUID) -> set[UUID]
```

Returns set of draft IDs that have active (incomplete) matches in the event.

### `count_incomplete_matches_by_event`

```python
async def count_incomplete_matches_by_event(event_id: UUID) -> int
```

Counts matches that have not been completed for an event.

### `get_event_context`

```python
async def get_event_context(match_id: UUID) -> tuple[UUID, UUID, StageFormat, UUID, UUID, UUID] | None
```

Returns `(event_id, group_id, stage_format, bracket_id, stage_id, group_id)` for a match. Used for permission checks.

### `list_by_event`

```python
async def list_by_event(
    event_id: UUID,
    offset: int,
    limit: int,
    active: bool | None = None,
) -> Sequence[Match]
```

Lists matches for an event with optional active/incomplete filter.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_slots` | `Match.slots` |
| `load_group` | `Match.group` |
