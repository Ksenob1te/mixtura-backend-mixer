# mixer-service — Agent Instructions

## Commands

```
python start.py              # Run app (requires RabbitMQ, Postgres, Redis)
alembic upgrade head         # Apply migrations
alembic revision -m "msg"    # Create migration
docker compose -f docker-compose.dev.yaml up -d   # Start Postgres + Redis
pytest                       # Run tests (asyncio_mode = auto)
```

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
  infra/
    postgre/        # SQLAlchemy ORM models + repo implementations
    rabbit/
      main.py       # FastStream app, lifespan, broker, error middleware
      api/          # Queue handlers — inject service via Depends
    redis/          # Redis engine + TeamFormationVariantStore
    clients/        # External: rating, mix_balancer, tournament_balancer
  dependency.py     # All DI wiring (repo → service → handler)
```

**Key pattern:** API handlers call `service.method(command)` directly. No usecase layer. All services in `src/core/services/` receive repository protocols in `__init__`.

## Important Conventions

- **Auth/perms:** `src/core/interfaces/repo/access.py` — only event-related permission bits (24-31) and restrictions (1-2). Services call `is_same_server()` and `has_event_admin_permission()`.
- **Transactions:** One `AsyncSession` per message via `Depends`. `DomainException` triggers auto-rollback in middleware (`main.py`).
- **Repositories:** Protocol in `core/interfaces/repo/`, implementation in `infra/postgre/repo/`. `BaseRepository` provides generic CRUD.
- **External balancers:** `mix_balancer` and `tournament_balancer` clients communicate via RabbitMQ, not HTTP.
- **Team formation variants:** Cached in Redis with TTL (default 3600s).
- **Alembic:** DB URL comes from `env.postgres.url` in `alembic/env.py`, not from `alembic.ini`.

## Services (src/core/services/)

| Service | Methods |
|---------|---------|
| `EventService` | create, get, list, update, activate, open/close_registration, cancel, complete |
| `ApplicationService` | submit, review, get, list |
| `OrganizerService` | list, add, remove |
| `PlayerService` | list, update_status, remove |
| `DraftService` | create, get, list |
| `TeamService` | list |
| `TeamFormationService` | run, get, choose_variant |
| `MatchService` | setup, record_result, get, list |
| `SettingsService` | add/remove_integration, add/update/remove_game_role, add/update/remove_custom_field, update_time_settings, get_application_form_settings |

## Quirks

- Python 3.13+ required (`pyproject.toml`).
- `pytest.ini` sets `asyncio_mode = auto` — no `@pytest.mark.asyncio` needed.
- The `service/` folder under `core/` is a leftover placeholder; real code is in `services/` (plural).
