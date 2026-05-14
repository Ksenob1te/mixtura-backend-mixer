# ApplicationTimeSettingsRepository

**Protocol:** `src/core/interfaces/repo/application_time_settings.py`
**Implementation:** `src/infra/postgre/repo/application_time_settings.py`
**Model:** `ApplicationTimeSettings` ([models/application-time-settings.md](../models/application-time-settings.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> ApplicationTimeSettings \| None` | |
| `get_list` | `(offset, limit, options, *where) -> Sequence[ApplicationTimeSettings]` | |
| `create` | `(dto: ApplicationTimeSettingsCreate) -> ApplicationTimeSettings` | |
| `update` | `(dto: ApplicationTimeSettingsUpdate) -> ApplicationTimeSettings` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get_by_event_id`

```python
async def get_by_event_id(event_id: UUID, load_event: bool) -> ApplicationTimeSettings | None
```

Finds time settings by event ID. Note: `load_event` has no default — must be explicitly specified.

### `delete_by_event_id`

```python
async def delete_by_event_id(event_id: UUID) -> None
```

Deletes time settings for a given event. Returns `None` (not `bool`).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_event` | `ApplicationTimeSettings.event` |
