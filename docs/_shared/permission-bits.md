# Permission Bits

- **File:** `src/core/interfaces/repo/access.py`

## Overview
Права и ограничения кодируются битовыми масками в `AccessDataRequest`. Permission биты (24-31) определяют административные права на события. Restriction биты (1-2) определяют запреты на участие.

## Permission Bits (24-31)

| Constant | Bit | Value | Description |
|----------|-----|-------|-------------|
| `P_EVENT_CREATE` | 24 | `1 << 24` | Создание нового события |
| `P_EVENT_ADMIN_VIEW` | 25 | `1 << 25` | Просмотр событий и их данных (включая непубличные) |
| `P_EVENT_ADMIN_UPDATE` | 26 | `1 << 26` | Редактирование настроек события, активация, регистрация, отмена, завершение |
| `P_EVENT_ADMIN_MANAGE_ORGANIZERS` | 27 | `1 << 27` | Добавление/удаление организаторов |
| `P_EVENT_ADMIN_MANAGE_PLAYERS` | 28 | `1 << 28` | Управление игроками: review applications, update status, remove, create draft |
| `P_EVENT_ADMIN_MANAGE_BRACKET` | 29 | `1 << 29` | Управление bracket: setup matches, record results, team formation |
| `P_EVENT_ADMIN_CANCEL` | 30 | `1 << 30` | Отмена события |
| `P_EVENT_ADMIN_COMPLETE` | 31 | `1 << 31` | Завершение события |

## Restriction Bits (1-2)

| Constant | Bit | Value | Description |
|----------|-----|-------|-------------|
| `R_MIX_BAN` | 1 | `1 << 1` | Запрет на участие в single match events |
| `R_TOURNAMENT_BAN` | 2 | `1 << 2` | Запрет на участие в tournament events |

## Helper Functions

### `has_permission(mask: int, bit: int) -> bool`
Проверяет, установлен ли конкретный бит прав в маске.
```python
return (mask & bit) != 0
```

### `has_restriction(mask: int, bit: int) -> bool`
Проверяет, установлен ли конкретный бит ограничения в маске.
```python
return (mask & bit) != 0
```

### `is_same_server(access: AccessDataRequest, event_server_id: UUID) -> bool`
Проверяет, совпадает ли `server_id` запроса с `server_id` события.
```python
return access.server_id == event_server_id
```

### `has_event_admin_permission(access: AccessDataRequest, event_server_id: UUID, bit: int) -> bool`
Комбинированная проверка: сервер совпадает И бит права установлен.
```python
return is_same_server(access, event_server_id) and has_permission(access.permission_mask, bit)
```

## Permission Check Pattern
Во всех сервисах используется единый паттерн проверки доступа:

```python
# 1. Проверка сервера
if not is_same_server(cmd.access_data, event.server_id):
    raise ForbiddenException("Event belongs to a different server")

# 2. Проверка организаторства
is_organizer = any(o.member_id == cmd.access_data.member_id for o in event.organizers)

# 3. Проверка admin-права
has_admin = has_event_admin_permission(cmd.access_data, event.server_id, P_EVENT_ADMIN_XXX)

# 4. Итоговая проверка
if not is_organizer and not has_admin:
    raise ForbiddenException("Only organizer or admin can XXX")
```

Организатор — это запись в `Organizer` с `member_id` пользователя. Организатор имеет все права на своё событие без необходимости соответствующих permission битов.
