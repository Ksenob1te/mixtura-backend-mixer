# MatchSlotRepository

**Protocol:** `src/core/interfaces/repo/match_slot.py`
**Implementation:** `src/infra/postgre/repo/match_slot.py`
**Model:** `MatchSlot` ([models/match-slot.md](../models/match-slot.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> MatchSlot \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[MatchSlot]` | |
| `create` | `(dto: MatchSlotCreate) -> MatchSlot` | |
| `update` | `(dto: MatchSlotCreate) -> MatchSlot` | Uses `MatchSlotCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_score: bool = False) -> MatchSlot | None
```

### `list_by_match`

```python
async def list_by_match(match_id: UUID) -> Sequence[MatchSlot]
```

Returns all slots for a given match (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_score` | `MatchSlot.score` |
