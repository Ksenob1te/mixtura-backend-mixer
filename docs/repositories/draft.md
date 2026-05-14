# DraftRepository

**Protocol:** `src/core/interfaces/repo/draft.py`
**Implementation:** `src/infra/postgre/repo/draft.py`
**Model:** `Draft` ([models/draft.md](../models/draft.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Draft \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Draft]` | |
| `create` | `(dto: DraftCreate) -> Draft` | |
| `update` | `(dto: DraftUpdate) -> Draft` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_drafted_players: bool = False) -> Draft | None
```

### `list_by_event`

```python
async def list_by_event(event_id: UUID, offset: int, limit: int) -> Sequence[Draft]
```

Lists drafts for a given event with pagination.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_drafted_players` | `Draft.drafted_players` |
