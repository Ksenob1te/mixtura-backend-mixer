# EventRepository

**Protocol:** `src/core/interfaces/repo/event.py`
**Implementation:** `src/infra/postgre/repo/event.py`
**Model:** `Event` ([models/event.md](../models/event.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Event \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where, order_by) -> Sequence[Event]` | |
| `create` | `(dto: EventCreate) -> Event` | |
| `update` | `(dto: EventUpdate) -> Event` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_organizers: bool = False,
    load_integrations: bool = False,
    load_time_settings: bool = False,
    load_game_roles: bool = False,
    load_custom_fields: bool = False,
    load_applications: bool = False,
    load_teams: bool = False,
    load_drafts: bool = False,
    load_players: bool = False,
    load_brackets: bool = False,
) -> Event | None
```

Eager-loads related entities via `selectinload`/`joinedload`.

### `list_public`

```python
async def list_public(offset: int, limit: int) -> Sequence[Event]
```

Returns events with `is_public=True`, sorted by `created_at DESC`.

### `list_public_by_server`

```python
async def list_public_by_server(server_id: UUID, offset: int, limit: int) -> Sequence[Event]
```

Returns public events filtered by `server_id`, sorted by `created_at DESC`.

### `list_by_server`

```python
async def list_by_server(server_id: UUID, offset: int, limit: int) -> Sequence[Event]
```

Returns all events (public and private) for a given `server_id`, sorted by `created_at DESC`.

### `transition_status`

```python
async def transition_status(event_id: UUID, new_status: EventStatus) -> Event
```

Atomically transitions event status via `UPDATE ... WHERE id = ?`.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_organizers` | `Event.organizers` |
| `load_integrations` | `Event.required_integrations` |
| `load_time_settings` | `Event.time_settings` |
| `load_game_roles` | `Event.selected_game_roles` |
| `load_custom_fields` | `Event.custom_fields` |
| `load_applications` | `Event.applications` |
| `load_teams` | `Event.teams` |
| `load_drafts` | `Event.drafts` |
| `load_players` | `Event.event_players` |
| `load_brackets` | `Event.brackets` |
