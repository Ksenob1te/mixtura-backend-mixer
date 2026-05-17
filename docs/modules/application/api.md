# Application — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/application.py`
- **Service file:** `src/core/services/application.py`
- **Commands file:** `src/core/commands/application.py`
- **Results file:** `src/core/results/application.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.application.submit` | `SubmitApplicationCommand` | `ApplicationSubmitResult` | Подача заявки на участие |
| `event.application.get` | `GetApplicationCommand` | `ApplicationDetail` | Получение заявки по ID |
| `event.application.list` | `ListApplicationsCommand` | `list[ApplicationListItem]` | Список заявок события |
| `event.application.review` | `ReviewApplicationCommand` | `ApplicationReviewResult` | Рассмотрение заявки (approve/reject/waitlist) |

---

## Queue: `event.application.submit`

### Command: `SubmitApplicationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | Требуется `member_id` |
| `event_id` | `UUID` | Yes | ID события |
| `integrations` | `list[IntegrationPayload]` | No | Список интеграций (provider_name должен совпадать с required) |
| `filled_fields` | `list[FilledFieldPayload]` | No | Заполненные кастомные поля |
| `role_priorities` | `list[RolePriorityPayload]` | No | Роли с приоритетами |

**IntegrationPayload:** `integration_id` (UUID), `provider_id` (UUID), `provider_name` (str)
**FilledFieldPayload:** `custom_field_id` (UUID), `value` (str)
**RolePriorityPayload:** `role_id` (UUID), `priority` (int)

### Result: `ApplicationSubmitResult`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID заявки |
| `status` | `ApplicationStatus` | Статус (APPROVED если use_application=False, иначе PENDING) |
| `auto_approved` | `bool` | Авто-одобрение (когда use_application=False) |
| `player_id` | `UUID` | ID созданного EventPlayer |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `ForbiddenException` | `member_id is None` |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | `R_MIX_BAN` для SINGLE events |
| `ForbiddenException` | `R_TOURNAMENT_BAN` для TOURNAMENT events |
| `ConflictException` | Заявка уже существует |
| `BadRequestException` | Время регистрации не наступило или истекло |
| `BadRequestException` | Дубликаты custom fields |
| `BadRequestException` | Unknown custom field |
| `BadRequestException` | Отсутствуют required custom fields |
| `BadRequestException` | Отсутствуют required integrations |
| `BadRequestException` | Unknown game role |
| `BadRequestException` | Duplicate game role priority |

---

## Queue: `event.application.get`

### Command: `GetApplicationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `application_id` | `UUID` | Yes | ID заявки |
| `access_data` | `AccessDataRequest` | Yes | |

### Result: `ApplicationDetail`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID заявки |
| `event_id` | `UUID` | |
| `member_id` | `UUID` | |
| `status` | `ApplicationStatus` | |
| `role_priorities` | `list[ApplicationRolePriorityItem]` | Роли игрока |
| `filled_fields` | `list[ApplicationFilledFieldItem]` | Заполненные поля |
| `integrations` | `list[ApplicationIntegrationItem]` | Интеграции |
| `event_player_id` | `UUID \| None` | ID участника (если approved) |

### Access Rules
- Своя заявка — всегда доступна
- Организатор/admin — всегда доступна
- Viewer события — доступна

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Заявка не найдена |
| `ForbiddenException` | Нет доступа |

---

## Queue: `event.application.list`

### Command: `ListApplicationsCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `status` | `ApplicationStatus \| None` | No | Фильтр по статусу |
| `pagination` | `PaginationRequest` | No | |
| `sort_by` | `str` | No | Default: "created_at" |
| `sort_order` | `str` | No | Default: "desc" |

### Result: `list[ApplicationListItem]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID заявки |
| `member_id` | `UUID` | |
| `status` | `ApplicationStatus` | |
| `created_at` | `datetime` | Время подачи |
| `roles` | `list[ApplicationRoleItem]` | Роли: `role_id` (UUID), `game_role_id` (UUID\|None), `priority` (int) |
| `integrations` | `list[ApplicationIntegrationItem]` | Интеграции: `integration_id` (UUID), `provider_id` (UUID), `provider_name` (str) |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Нет доступа (не viewer и не admin) |

---

## Queue: `event.application.review`

### Command: `ReviewApplicationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `application_id` | `UUID` | Yes | |
| `status` | `ApplicationStatus` | Yes | APPROVED / REJECTED / WAITLIST |
| `role_priorities` | `list[RolePriorityPayload]` | No | Роли при approval |

### Result: `ApplicationReviewResult`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID заявки |
| `status` | `ApplicationStatus` | Новый статус |
| `player_id` | `UUID \| None` | ID EventPlayer (только при APPROVED) |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Заявка/событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `ForbiddenException` | Approval с другого сервера |
| `ConflictException` | EventPlayer уже в статусе PLAYING |
| `BadRequestException` | Unsupported application status |
