# PaginationRequest

- **File:** `src/core/commands/pagination.py`

## Role
Стандартный блок пагинации, используемый в командах list-операций.

## Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | `int \| None` | `None` | Номер страницы (1-indexed). Если `None` — пагинация не применяется, возвращаются все записи. |
| `page_size` | `int` | `50` | Количество записей на странице. |

## Usage
В сервисах обрабатывается как:
```python
offset = (cmd.pagination.page - 1) * cmd.pagination.page_size if cmd.pagination.page else 0
limit = cmd.pagination.page_size
```
