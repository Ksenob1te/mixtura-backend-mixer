# ApplicationRepository

**Protocol:** `src/core/interfaces/repo/application.py`
**Implementation:** `src/infra/postgre/repo/application.py`
**Model:** `Application` ([models/application.md](../models/application.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Application \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where, order_by) -> Sequence[Application]` | |
| `create` | `(dto: ApplicationCreate) -> Application` | |
| `update` | `(dto: ApplicationUpdate) -> Application` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_filled_fields: bool = False,
    load_integrations: bool = False,
    load_event_player: bool = False,
) -> Application | None
```

### `get_by_event_and_member`

```python
async def get_by_event_and_member(event_id: UUID, member_id: UUID) -> Application | None
```

Finds application by event and member pair.

### `list_by_event`

```python
async def list_by_event(
    event_id: UUID,
    offset: int,
    limit: int,
    status: ApplicationStatus | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    load_event_player_with_roles: bool = False,
    load_integrations: bool = False,
) -> Sequence[Application]
```

Lists applications for an event with optional status filter, sorting, and eager loading.

### `count_by_event_and_status`

```python
async def count_by_event_and_status(event_id: UUID, status: ApplicationStatus) -> int
```

Counts applications for an event filtered by status.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_filled_fields` | `Application.filled_fields` |
| `load_integrations` | `Application.integrations` |
| `load_event_player` | `Application.event_player` |
| `load_event_player_with_roles` | `Application.event_player` + `EventPlayer.player_roles` |
