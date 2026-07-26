# Health — Queue Contracts

## Overview
- **Handler file:** `src/app/rabbit/api/health.py`
- **Commands file:** `src/core/commands/health.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.health` | `HealthRequest` | `StatusResponse` | Проверка работоспособности сервиса |

---

## Queue: `event.health`

### Command: `HealthRequest`
Пустая команда (без полей).

### Result: `StatusResponse`
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | `str` | `"ok"` | Статус сервиса |

### Behavior
- Не использует сервисный слой
- Не требует авторизации
- Возвращает `ResponseMessage[StatusResponse]` со статусом 200
- Используется для health check / liveness probe

### Exceptions
Нет. Всегда возвращает success.
