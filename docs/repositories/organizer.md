# OrganizerRepository

**Protocol:** `src/core/interfaces/repo/organizer.py`
**Implementation:** `src/infra/postgre/repo/organizer.py`
**Model:** `Organizer` ([models/organizer.md](../models/organizer.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Organizer \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Organizer]` | |
| `create` | `(dto: OrganizerCreate) -> Organizer` | |
| `update` | `(dto: OrganizerCreate) -> Organizer` | Uses `OrganizerCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_event: bool = False) -> Organizer | None
```

### `list_by_event`

```python
async def list_by_event(event_id: UUID) -> Sequence[Organizer]
```

Returns all organizers for a given event (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_event` | `Organizer.event` |
