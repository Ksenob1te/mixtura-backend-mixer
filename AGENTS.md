# mixer-service — Agent Instructions

## Commands

```
uv run python start.py       # Run app (requires RabbitMQ, Postgres, Redis)
uv run alembic upgrade head  # Apply migrations
uv run alembic revision -m "msg"  # Create migration
docker compose -f docker-compose.dev.yaml up -d   # Start Postgres + Redis
uv run pytest                # Run tests (requires Docker for Postgres testcontainers)
uv run pytest tests/repo     # Run repository tests only when repository code changes
```

Use `uv run` for Python commands.

Requires `.env` (copy from `.env.example`). Env loaded via `pydantic-settings` in `src/env_config.py`.

## Architecture

**Message-driven microservice** — FastStream + RabbitMQ, no HTTP. Each queue maps to one service method.

```
src/
  core/
    commands/       # Input DTOs (Pydantic)
    models/         # Domain models (Pydantic)
    results/        # Output DTOs
    exceptions.py   # DomainException, BadRequest, NotFound, Conflict, Forbidden
    response.py     # ResponseMessage wrapper
    services/       # Business logic classes (all scenarios)
    interfaces/
      repo/         # Protocol interfaces + access.py (permissions)
  app/
    rabbit/
      main.py       # FastStream app, lifespan, broker, error middleware
      api/          # Queue handlers — inject service via Depends
      models/       # External message schemas (wire contract)
  infra/
    rabbit/
      rpc_client.py # Async RPC client (RabbitMQ request/reply)
    postgre/        # SQLAlchemy ORM models + repo implementations
    redis/          # Redis engine + TeamFormationVariantStore
    clients/        # External: rating, mix_balancer, tournament_balancer
  config/           # Optional state machine config (INI/YAML)

**Key pattern:** API handlers call `service.method(command)` directly. No usecase layer. All services in `src/core/services/` receive repository protocols in `__init__`.

Flow: `api -|commands/results|> services -|dtos|> repos -> orm models`.

## Important Conventions

- **Documentation:** When making code changes, you MUST update `docs/INDEX.md` and the corresponding documentation files. For looking up methods, services, repositories, and APIs, start by reading `docs/INDEX.md` and only load files for the relevant module — do not load the entire documentation tree. Use source code only for clarifying implementation details.
- **Auth/perms:** `src/core/interfaces/repo/access.py` — only event-related permission bits (24-31) and restrictions (1-2). Services call `is_same_server()` and `has_event_admin_permission()`.
- **Transactions:** One `AsyncSession` per message via `Depends`. `DomainException` triggers auto-rollback in middleware (`main.py`).
- **Repositories:** Protocol in `core/interfaces/repo/`, implementation in `infra/postgre/repo/`. `BaseRepository` provides generic CRUD.
- **Repository tests:** Run `uv run pytest tests/repo` only when repository protocols, implementations, or ORM mappings change.
- **External balancers:** `mix_balancer` and `tournament_balancer` clients communicate via RabbitMQ, not HTTP.
- **Team formation variants:** Cached in Redis with TTL (default 3600s).
- **Alembic:** DB URL comes from `env.postgres.url` in `alembic/env.py`, not from `alembic.ini`.
- **Architecture guide:** If you encounter a reusable solution pattern or a recurring anti-pattern worth documenting, **propose it to the user** for addition to `docs/guides/architecture-guide.md`. Don't add entries unilaterally — the user decides what goes into the guide. Keep the guide — not this file — as the living record of architectural decisions and conventions.

## Services (src/core/services/)

Services contain business scenarios and coordinate validation, permissions, repository calls, and external clients. Keep API handlers thin and persistence logic in repositories.

Update this table whenever adding, removing, or renaming services or service methods.

| Service | Functional area | Methods |
|---------|-----------------|---------|
| `EventService` | Event lifecycle, registration state, and visibility rules | create, get, list, update, activate, open/close_registration, cancel, complete |
| `ApplicationService` | Player applications and organizer review decisions | submit, review, get, list |
| `OrganizerService` | Event organizer membership management | list, add, remove |
| `PlayerService` | Event player roster and participation status | list, bulk_get, update_status, remove |
| `DraftService` | Draft creation and draft lookup for events | create, get, list |
| `TeamService` | Event team lookup | list |
| `TeamFormationService` | Team formation runs, cached variants, and variant selection | run, get, choose_variant |
| `MatchService` | Match setup, result recording, and match lookup | setup, record_result, get, list |
| `SettingsService` | Event integrations, game roles, custom fields, and application form settings | add/remove_integration, add/update/remove_game_role, add/update/remove_custom_field, update_time_settings, get_application_form_settings |

## Quirks

- Python 3.13+ required (`pyproject.toml`).
- `pytest.ini` loads `.env`, sets `asyncio_mode = auto`, and uses session-scoped asyncio loops; no `@pytest.mark.asyncio` needed.
