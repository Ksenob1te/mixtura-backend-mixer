# ApplicationCustomFieldRepository

**Protocol:** `src/core/interfaces/repo/application_custom_field.py`
**Implementation:** `src/infra/postgre/repo/application_custom_field.py`
**Model:** `ApplicationCustomField` ([models/application-custom-field.md](../models/application-custom-field.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> ApplicationCustomField \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[ApplicationCustomField]` | |
| `create` | `(dto: ApplicationCustomFieldCreate) -> ApplicationCustomField` | |
| `update` | `(dto: ApplicationCustomFieldUpdate) -> ApplicationCustomField` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_event: bool) -> ApplicationCustomField | None
```

Note: `load_event` has no default — must be explicitly specified.

### `list_by_event`

```python
async def list_by_event(event_id: UUID) -> Sequence[ApplicationCustomField]
```

Returns all custom fields for a given event (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_event` | `ApplicationCustomField.event` |
