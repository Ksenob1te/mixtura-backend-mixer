# ApplicationIntegrationRepository

**Protocol:** `src/core/interfaces/repo/application_integration.py`
**Implementation:** `src/infra/postgre/repo/application_integration.py`
**Model:** `ApplicationIntegration` ([models/application-integration.md](../models/application-integration.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> ApplicationIntegration \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[ApplicationIntegration]` | |
| `create` | `(dto: ApplicationIntegrationCreate) -> ApplicationIntegration` | |
| `update` | `(dto: ApplicationIntegrationCreate) -> ApplicationIntegration` | Uses `ApplicationIntegrationCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_application: bool = False) -> ApplicationIntegration | None
```

### `list_by_application`

```python
async def list_by_application(application_id: UUID) -> Sequence[ApplicationIntegration]
```

Returns all integrations for a given application (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_application` | `ApplicationIntegration.application` |
