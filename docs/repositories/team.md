# TeamRepository

**Protocol:** `src/core/interfaces/repo/team.py`
**Implementation:** `src/infra/postgre/repo/team.py`
**Model:** `Team` ([models/team.md](../models/team.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Team \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Team]` | |
| `create` | `(dto: TeamCreate) -> Team` | |
| `update` | `(dto: TeamUpdate) -> Team` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_event: bool = False,
    load_players: bool = False,
) -> Team | None
```

### `list_by_event`

```python
async def list_by_event(event_id: UUID, offset: int, limit: int) -> Sequence[Team]
```

Lists teams for a given event with pagination.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_event` | `Team.event` |
| `load_players` | `Team.players` |
