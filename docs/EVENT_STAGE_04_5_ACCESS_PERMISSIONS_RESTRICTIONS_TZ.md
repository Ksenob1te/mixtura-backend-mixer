# ТЗ Для Агента: Этап 4.5. Фикс Permissions И Restrictions

## Цель
Исправить уже реализованные в этапах 1-4 проверки `permission_mask` и `restriction_mask`, чтобы Event Service интерпретировал маски точно так же, как Server Service. Этот этап должен быть выполнен после этапов 1-4 и до этапа 5.

## Почему Нужен Этап 4.5
- Этапы 1-4 уже реализованы и используют access helpers в `src/core/usecases/_access.py`.
- Текущий helper содержит ручные bit constants для event permissions.
- Server Service сериализует permission mask не по отдельной таблице Event Service, а по порядку enum `PERMISSION` из `src/infra/postgre/static/permissions.py`.
- Поэтому Event Service должен повторять server enum order или вычислять bit position из локального mirror enum. Нельзя использовать произвольные `1 << N`.

## Canonical Server Sources
Использовать как источник истины:

- `C:\Users\dmela\Desktop\desktop\programming\mixtura-backend-server\src\infra\postgre\static\permissions.py`
- `C:\Users\dmela\Desktop\desktop\programming\mixtura-backend-server\src\infra\postgre\static\restrictions.py`
- `C:\Users\dmela\Desktop\desktop\programming\mixtura-backend-server\src\domain\service\access_control.py`

## Как Server Service Кодирует Permissions
В Server Service `PERMISSION.serialize_permission_codes(...)` делает:

```python
mask = 0
for i, member in enumerate(PERMISSION):
    if member in permissions:
        mask |= (1 << i)
```

`PERMISSION.check_permission(mask, permission)` находит позицию через `list(PERMISSION).index(permission)`.

Следовательно, Event Service должен проверять те же биты, что и Server Service enum order.

## Canonical Permission Order
Порядок из Server Service на момент фиксации:

| Bit | Code |
| --- | --- |
| 0 | `administrator` |
| 1 | `edit_name` |
| 2 | `edit_roles` |
| 3 | `create_virtual` |
| 4 | `migrate_members` |
| 5 | `kick_members` |
| 6 | `create_custom` |
| 7 | `delete_custom` |
| 8 | `edit_all_customs` |
| 9 | `edit_server_roles` |
| 10 | `edit_server_public` |
| 11 | `edit_server_name` |
| 12 | `edit_server_description` |
| 13 | `edit_server_banner` |
| 14 | `edit_server_icon` |
| 15 | `edit_server_game` |
| 16 | `delete_server` |
| 17 | `edit_role_set` |
| 18 | `edit_rating_set` |
| 19 | `edit_invites` |
| 20 | `restrict_server_ban` |
| 21 | `restrict_mix_ban` |
| 22 | `restrict_tournament_ban` |
| 23 | `restrict_self_edit_name` |
| 24 | `event_create` |
| 25 | `event_admin_view` |
| 26 | `event_admin_update` |
| 27 | `event_admin_manage_organizers` |
| 28 | `event_admin_manage_players` |
| 29 | `event_admin_manage_bracket` |
| 30 | `event_admin_cancel` |
| 31 | `event_admin_complete` |

Важно: create permission называется `event_create`. Если в Server Service сейчас встречается `event_admin_create`, это опечатка и ее не нужно переносить в Event Service docs/code.

## Canonical Restriction Order
Порядок из Server Service `RESTRICTION`:

| Bit | Code | Event Service Usage |
| --- | --- | --- |
| 0 | `server_ban` | запрещает создание event, join/application и organizer/admin действия в этом server context |
| 1 | `mix_ban` | запрещает участие в одиночном/mix event |
| 2 | `tournament_ban` | запрещает участие в tournament event |
| 3 | `self_edit_name` | не влияет на Event Service, пока Event Service не меняет nickname |

Restriction mask и permission mask являются разными масками. Permission codes `restrict_server_ban`, `restrict_mix_ban`, `restrict_tournament_ban`, `restrict_self_edit_name` означают право назначать restrictions в Server Service; Event Service не должен использовать их как active restrictions.

## Требуемая Реализация
- Переписать `src/core/usecases/_access.py`, чтобы убрать ручные ошибочные биты для permissions.
- Добавить локальный mirror enum или другой явный механизм, который повторяет `PERMISSION` order из Server Service.
- Добавить локальный mirror enum или явный механизм для `RESTRICTION` order.
- Проверять permissions через helper, который вычисляет bit index по enum order, например `1 << list(PermissionCode).index(code)`.
- Проверять restrictions аналогично через `RestrictionCode` order.
- Сохранить canonical code `event_create`, но исправить bit position `P_EVENT_CREATE` на bit 24 по Server Service enum order.
- Проверить error messages и docs references: они должны использовать `event_create`, а не `event_admin_create`.
- Не импортировать Server Service из Event Service runtime-кода.
- Не обращаться в Server Service и не вычислять permissions самостоятельно. Event Service только интерпретирует уже полученные masks.

## Access Semantics После Фикса
- `administrator`: Server Service сам разворачивает administrator/owner в full mask через `AccessControlService._compute_overwrites_mask(...)`. Event Service не обязан отдельно special-case `administrator`, потому что event permission bits уже будут выставлены в полученном mask.
- `event_create`: требуется для создания мероприятия, если создание не открыто всем участникам пространства.
- `event_admin_view`: внешний admin override для просмотра непубличных/admin данных без локальной роли organizer.
- `event_admin_update`: внешний admin override для изменения настроек/статуса чужого event.
- `event_admin_manage_organizers`: внешний admin override для восстановления/замены organizers.
- `event_admin_manage_players`: внешний admin override для заявок, игроков и составов.
- `event_admin_manage_bracket`: внешний admin override для bracket/stage/group/match/result setup.
- `event_admin_cancel`: внешний admin override для отмены event.
- `event_admin_complete`: внешний admin override для завершения stages/events.
- Локальный `Organizer` сохраняет полную власть над своим event без server permissions.
- `server_ban` блокирует создание, join/application и organizer/admin действия в этом server context.
- `mix_ban` и `tournament_ban` блокируют участие, но не должны автоматически блокировать organizer-действия, если organizer не участвует как player.
- `self_edit_name` игнорируется Event Service.

## Файлы Для Проверки И Правки
Минимально проверить:

- `src/core/usecases/_access.py`
- `src/core/usecases/event.py`
- `src/core/usecases/organizer.py`
- `src/core/usecases/application.py`
- `src/core/usecases/player.py`
- `docs/SERVER_GATEWAY_EVENT_INTEGRATION.md`
- `docs/EVENT_STAGE_02_EXTERNAL_CONTRACTS_TZ.md`
- `docs/EVENT_STAGE_03_EVENT_MANAGEMENT_TZ.md`
- `docs/EVENT_MODULE_IMPLEMENTATION_PLAN.md`
- `docs/EVENT_AGENT_IMPLEMENTATION_CONTEXT.md`

## Не Делать
- Не добавлять прямой dependency на `mixtura-backend-server`.
- Не добавлять `ServerClient`, `SpaceClient`, `IdentityClient` в Event Service.
- Не менять Server Service в рамках этого этапа.
- Не менять Alembic и PostgreSQL schema.
- Не писать и не чинить tests; testing остается этапом 10.
- Не менять бизнес-логику этапов 1-4 шире, чем требуется для корректной интерпретации masks.

## Acceptance Checklist
- Event Service permission helpers используют canonical Server Service enum order.
- Event permission bits соответствуют `1 << 24` ... `1 << 31`.
- Restriction bits соответствуют `server_ban=1 << 0`, `mix_ban=1 << 1`, `tournament_ban=1 << 2`, `self_edit_name=1 << 3`.
- В Event Service нет ссылок на `event_admin_create`; используется `event_create`.
- Локальный organizer по-прежнему может управлять своим event без server permissions.
- Server-admin override работает только через `event_admin_*` permissions.
- `server_ban`, `mix_ban`, `tournament_ban` применяются по семантике выше.
- `uv run mypy src` проходит или оставшиеся ошибки не относятся к этому этапу.

## Команды Проверки
- `uv run mypy src`
