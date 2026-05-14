# RequiredIntegrationRepository

**Protocol:** `src/core/interfaces/repo/required_integration.py`
**Implementation:** `src/infra/postgre/repo/required_integration.py`
**Model:** `RequiredIntegration` ([models/required-integration.md](../models/required-integration.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> RequiredIntegration \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[RequiredIntegration]` | |
| `create` | `(dto: RequiredIntegrationCreate) -> RequiredIntegration` | |
| `update` | `(dto: RequiredIntegrationUpdate) -> RequiredIntegration` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_event: bool) -> RequiredIntegration | None
```

Note: `load_event` has no default — must be explicitly specified.

### `list_by_event`

```python
async def list_by_event(event_id: UUID) -> Sequence[RequiredIntegration]
```

Returns all required integrations for a given event (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_event` | `RequiredIntegration.event` |
