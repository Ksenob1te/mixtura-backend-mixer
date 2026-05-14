# FilledApplicationFieldRepository

**Protocol:** `src/core/interfaces/repo/filled_application_field.py`
**Implementation:** `src/infra/postgre/repo/filled_application_field.py`
**Model:** `FilledApplicationField` ([models/filled-application-field.md](../models/filled-application-field.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> FilledApplicationField \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[FilledApplicationField]` | |
| `create` | `(dto: FilledApplicationFieldCreate) -> FilledApplicationField` | |
| `update` | `(dto: FilledApplicationFieldCreate) -> FilledApplicationField` | Uses `FilledApplicationFieldCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_application: bool = False,
    load_custom_field: bool = False,
) -> FilledApplicationField | None
```

### `list_by_application`

```python
async def list_by_application(application_id: UUID) -> Sequence[FilledApplicationField]
```

Returns all filled fields for a given application (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_application` | `FilledApplicationField.application` |
| `load_custom_field` | `FilledApplicationField.custom_field` |
