# Response Wrapper

- **File:** `src/core/response.py`

## ResponseMessage<T>
Универсальная обёртка для всех ответов сервиса.

| Field | Type | Description |
|-------|------|-------------|
| `status` | `int` | Код статуса. `200` — успех, `400/403/404/409/500` — ошибка. |
| `message` | `T` | Полезная нагрузка (результат операции или ошибка). |

### Success Response
```json
{
  "status": 200,
  "message": { /* результат операции */ }
}
```

### Error Response (via middleware)
```json
{
  "status": 400,
  "message": {
    "message": "Description of the error"
  }
}
```

## ErrorResponse
Тело ошибки, возвращаемое middleware при `DomainException`.

| Field | Type | Description |
|-------|------|-------------|
| `message` | `str` | Текст ошибки из `DomainException.message` |

## StatusResponse
Пустой ответ для операций без возвращаемого значения (remove, delete).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | `str` | `"ok"` | Статус операции. |
