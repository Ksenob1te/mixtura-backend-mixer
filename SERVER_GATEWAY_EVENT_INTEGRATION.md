# Интеграция Event Service с Gateway и Server Service

## Источники
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/models/request.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/api/member.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/api/core.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/api/game_role.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/api/rating.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/domain/api/custom.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/infra/postgre/static/permissions.py`
- `C:/Users/dmela/Desktop/desktop/programming/mixtura-backend-server/src/infra/postgre/static/restrictions.py`

## Общий Принцип
- REST и пользовательская аутентификация остаются в Gateway.
- Gateway должен получить контекст доступа пользователя к пользовательскому пространству через Server Service и передать его в команды Event Service.
- Event Service не должен ходить напрямую в БД Server Service и не должен самостоятельно вычислять роли, права и ограничения пользователя.
- Event Service хранит `server_id` у события и всех связанных aggregate root, чтобы обеспечить изоляцию мероприятий по пользовательскому пространству.
- Event Service дополнительно проверяет собственные правила мероприятия: организаторы события, статус события, окно регистрации, состав заявок, состав выборки и матчевые ограничения.

## Общие DTO
Server Service использует общий envelope для ответов:

```python
ResponseMessage[T](
    status=int,
    message=T,
)
```

Основной authorization envelope для входящих команд:

```python
AccessDataRequest(
    member_id=UUID | None,
    server_id=UUID,
    permission_mask=int,
    restriction_mask=int,
)
```

Event Service должен использовать совместимый `access_data` во всех командах, которым нужен контекст пространства и участника.

## Получение Access Context
- Queue: `member.by_user`.
- Request: `GetMemberByUserRequest(server_id=UUID, user_id=UUID)`.
- Response: `AccessResponse(member=MemberResponse | None, permission_mask=int, restriction_mask=int)`.
- `member=None` означает, что пользователь не является участником пространства; для приватного пространства Server Service возвращает ошибку.
- Для большинства event-команд `member_id` должен быть не `None`; публичные read-only сценарии могут принимать только `server_id` или `access_data` с `member_id=None`, если это явно разрешено use case.
- Gateway может кэшировать `permission_mask` и `restriction_mask` только в рамках короткого запроса; Event Service не должен считать эти маски долгоживущим состоянием.

## Server Service RPC, Нужные Event Service
- `server.get_info`: проверить существование `server_id` и получить связанные `rating_set`, `role_set`, `games`.
- `member.by_user`: получить `member_id`, `permission_mask`, `restriction_mask` по `server_id + user_id`.
- `member.get`: получить `MemberResponse` по `target_member_id`; Event Service должен проверить, что `member.server_id == access_data.server_id`.
- `member.list`: получить участников пространства для ручного выбора участников мероприятия.
- `role_set.get_by_server`: получить доступные игровые роли пространства, включая `min_in_team`, `max_in_team`, `hidden`.
- `rating_set.get_by_server`: получить рейтинговую шкалу пространства, включая `min_rating`, `max_rating` и threshold-ы.
- `custom.get_by_member`: получить экспертные/open ratings участника по игровым ролям перед вызовом `rating.effective.calculate`.
- `server.global.permissions` и `server.global.restrictions`: нужны в основном Gateway/admin UI, но могут использоваться тестами контрактов.

## Рекомендации Для Event RPC Commands
- `CreateEventCommand`, `UpdateEventCommand`, `OpenRegistrationCommand`, `CancelEventCommand` должны включать `access_data`.
- `SubmitApplicationCommand` должен включать `access_data`; `member_id=None` допустим только если будет отдельно реализована внешняя гостевая регистрация.
- `ReviewApplicationCommand`, `CreateDraftCommand`, `RunTeamFormationCommand`, `ChooseTeamFormationVariantCommand`, `GenerateBracketCommand`, `RecordMatchResultCommand` должны включать `access_data` и проверять organizer права внутри Event Service.
- Public list/get команды могут принимать `server_id`, pagination/filter поля и не требовать `access_data`, если возвращают только публичные события и публичные поля.
- Private list/get команды должны принимать `access_data` и проверять членство в пространстве.

## Права И Ограничения
Текущий Server Service содержит общие permission flags, но не содержит event-specific прав вроде `create_event`, `edit_events`, `manage_event_applications` или `record_event_results`.

Существующие полезные permission flags:

```python
administrator
edit_role_set
edit_rating_set
restrict_mix_ban
restrict_tournament_ban
```

Существующие restriction flags:

```python
server_ban
mix_ban
tournament_ban
self_edit_name
```

Для MVP нельзя перегружать `edit_role_set`, `edit_rating_set` или `create_custom` как права управления мероприятиями. Нужно выбрать один из вариантов:

- Добавить event-specific permissions в Server Service и использовать их в Gateway/Event Service.
- Для первого среза разрешить создание мероприятия любому участнику пространства без `server_ban`, а дальнейшее управление проверять только через локальную таблицу organizers в Event Service.

Рекомендуемый MVP-вариант: локальные organizers в Event Service плюс обязательная проверка членства и restrictions. Event-specific permissions можно добавить позже, когда будет утверждена административная модель.

## Проверка Restrictions В Event Service
- `server_ban`: запрещать создание, вступление, подачу заявки и любые organizer-действия в мероприятиях этого пространства.
- `mix_ban`: запрещать участие в одиночном матче или mix-событии; organizer-действия можно разрешать только если бизнес-правила допускают неучаствующих организаторов.
- `tournament_ban`: запрещать участие в турнирном событии; organizer-действия можно разрешать только если бизнес-правила допускают неучаствующих организаторов.
- `self_edit_name`: не влияет на Event Service, если Event Service не изменяет nickname участника.

## Open Rating Source
- Open/expert ratings для формирования команд должны приходить из `custom.get_by_member` или из локального event snapshot, если организатор переопределяет рейтинг на мероприятие.
- Перед вызовом балансировщика Event Service обязан вызвать `rating.effective.calculate` из `mixtura_ranker` и заменить open rating на `effective_rating`.
- Event Service должен сохранять оба значения в snapshot: исходный open rating и рассчитанный effective rating.

## Важные Риски Контракта
- `member.get` возвращает участника по id без server-specific request field, поэтому Event Service обязан проверять `server_id` в ответе.
- `role_set.get_by_server` и `rating_set.get_by_server` получают `server_id` из `access_data`; для внутренних проверок Event Service должен формировать service-level `access_data` или использовать Gateway-provided `access_data` текущего пользователя.
- Если Gateway передает устаревшие masks, Event Service может принять неверное решение. Поэтому masks должны вычисляться на Gateway непосредственно перед RPC-командой или Event Service должен иметь отдельный ServerClient для повторной проверки критических операций.
