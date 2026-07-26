# Domain Exceptions

- **File:** `src/core/exceptions.py`

## Overview
Все доменные исключения наследуются от `DomainException` и автоматически обрабатываются middleware в `src/app/rabbit/main.py`. При выбросе исключения происходит автоматический rollback транзакции и возврат `ResponseMessage` с соответствующим HTTP-подобным статусом.

## Hierarchy

```
DomainException (base)
├── NotFoundException (404)
├── ForbiddenException (403)
├── BadRequestException (400)
├── ConflictException (409)
└── InternalLogicException (500)
```

## Exception Types

### `DomainException`
Базовый класс. Не используется напрямую в сервисах.

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP-подобный код статуса |
| `message` | `str` | Текст ошибки |

### `NotFoundException` (404)
Ресурс не найден по запросу.

**Типичные сценарии:**
- Event/Draft/Match/Application не найден по ID
- Организатор/игрок не найден в контексте события
- Вариант формирования команд не найден в кэше

### `ForbiddenException` (403)
У вызывающей стороны нет прав на операцию.

**Типичные сценарии:**
- `member_id is None` — требуется идентификация
- Нет permission бита (например, `P_EVENT_CREATE`)
- `server_id` запроса не совпадает с `server_id` события
- Restriction бит активен (`R_MIX_BAN`, `R_TOURNAMENT_BAN`)
- Не является организатором и нет admin-права

### `BadRequestException` (400)
Входные данные невалидны или операция невозможна в текущем контексте.

**Типичные сценарии:**
- Событие не в том статусе для операции
- Отсутствуют обязательные поля/интеграции
- Дубликаты в данных
- Все команды forfeit в одном матче

### `ConflictException` (409)
Конфликт с текущим состоянием ресурса.

**Типичные сценарии:**
- Application уже существует для данного участника
- Draft не в статусе OPEN для team formation
- Команды уже назначены на активный матч
- Event уже в терминальном статусе (COMPLETED/CANCELLED)

### `InternalLogicException` (500)
Неожиданная серверная ошибка логики. Используется редко.

## Error Response Format
При выбросе исключения middleware возвращает:
```json
{
  "status": 400,
  "message": {
    "message": "Текст ошибки"
  }
}
```
