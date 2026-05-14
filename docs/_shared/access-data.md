# AccessDataRequest

- **File:** `src/core/commands/access_data.py`

## Role
Стандартный блок авторизации, передаваемый в каждой команде. Содержит идентификацию участника, сервера и битовые маски прав/ограничений.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `member_id` | `UUID \| None` | Yes | Идентификатор участника. Может быть `None` для анонимных операций (просмотр публичных событий). |
| `server_id` | `UUID` | Yes | Идентификатор сервера, от имени которого выполняется запрос. |
| `permission_mask` | `int` | Yes | Битовая маска прав (permission bits 24-31). См. [Permission Bits](permission-bits.md). |
| `restriction_mask` | `int` | Yes | Битовая маска ограничений (restriction bits 1-2). См. [Permission Bits](permission-bits.md). |

## Usage
Присутствует практически во всех командах как поле `access_data`. Используется сервисами для:
- Проверки `server_id` через `is_same_server()`
- Проверки прав через `has_permission()` / `has_event_admin_permission()`
- Проверки ограничений через `has_restriction()`
