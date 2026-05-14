# BracketRepository

**Protocol:** `src/core/interfaces/repo/bracket.py`
**Implementation:** `src/infra/postgre/repo/bracket.py`
**Model:** `Bracket` ([models/bracket.md](../models/bracket.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Bracket \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Bracket]` | |
| `create` | `(dto: BracketCreate) -> Bracket` | |
| `update` | `(dto: BracketCreate) -> Bracket` | Uses `BracketCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_placements: bool = False,
    load_stages: bool = False,
) -> Bracket | None
```

### `list_by_event`

```python
async def list_by_event(event_id: UUID, offset: int, limit: int) -> Sequence[Bracket]
```

Lists brackets for a given event with pagination.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_placements` | `Bracket.placements` |
| `load_stages` | `Bracket.stages` |
