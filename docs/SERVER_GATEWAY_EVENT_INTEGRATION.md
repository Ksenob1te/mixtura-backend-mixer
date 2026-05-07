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
- Event Service не должен обращаться в Server Service напрямую, ходить напрямую в БД Server Service или самостоятельно вычислять роли, права и ограничения пользователя.
- Для внутренних RPC-команд `AccessDataRequest` заменяет пользовательский JWT: Event Service доверяет этому объекту как контексту доступа, подготовленному Gateway.
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

## Server Service RPC, Нужные Gateway
Event Service не вызывает эти RPC напрямую. Gateway вызывает их перед командой в Event Service и передает результат в request payload, когда use case требует внешний контекст.

- `server.get_info`: проверить существование `server_id` и получить связанные `rating_set`, `role_set`, `games`.
- `member.by_user`: получить `member_id`, `permission_mask`, `restriction_mask` по `server_id + user_id`.
- `member.get`: получить `MemberResponse` по `target_member_id`; Gateway или Event Service по переданным данным должен проверить, что `member.server_id == access_data.server_id`.
- `member.list`: получить участников пространства для ручного выбора участников мероприятия.
- `role_set.get_by_server`: получить доступные игровые роли пространства, включая `min_in_team`, `max_in_team`, `hidden`.
- `rating_set.get_by_server`: получить рейтинговую шкалу пространства, включая `min_rating`, `max_rating` и threshold-ы.
- `custom.get_by_member`: получить экспертные/open ratings участника по игровым ролям перед формированием rating snapshot.
- `server.global.permissions` и `server.global.restrictions`: нужны в основном Gateway/admin UI и тестам контрактов.

## Рекомендации Для Event RPC Commands
- `CreateEventCommand`, `UpdateEventCommand`, `OpenRegistrationCommand`, `CancelEventCommand` должны включать `access_data`.
- `SubmitApplicationCommand` должен включать `access_data`; `member_id=None` допустим только если будет отдельно реализована внешняя гостевая регистрация.
- `ReviewApplicationCommand`, `CreateDraftCommand`, `RunTeamFormationCommand`, `ChooseTeamFormationVariantCommand`, `GenerateBracketCommand`, `RecordMatchResultCommand` должны включать `access_data` и проверять локальную роль organizer внутри Event Service либо явное server-admin override permission.
- Public list/get команды могут принимать `server_id`, pagination/filter поля и не требовать `access_data`, если возвращают только публичные события и публичные поля.
- Private list/get команды должны принимать `access_data` и проверять членство в пространстве.

## Права И Ограничения
Server Service должен содержать event-specific permission flags, чтобы Gateway мог включать их в `AccessDataRequest.permission_mask` для Event Service. Эти permissions описывают внешние административные права на уровне пользовательского пространства и не ограничивают локального organizer конкретного мероприятия.

Существующие общие permission flags, которые не нужно перегружать event-семантикой:

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

Event-specific permissions для добавления в Server Service:

```python
event_create
event_admin_view
event_admin_update
event_admin_manage_organizers
event_admin_manage_players
event_admin_manage_bracket
event_admin_cancel
event_admin_complete
```

Семантика:

- `event_create`: создавать мероприятия в пользовательском пространстве, если создание не открыто всем участникам пространства.
- `event_admin_view`: просматривать непубличные мероприятия и административные данные мероприятий без локальной роли organizer.
- `event_admin_update`: административно изменять настройки и статус любого мероприятия пространства без локальной роли organizer.
- `event_admin_manage_organizers`: произвольно добавлять, удалять и заменять organizers любого мероприятия пространства.
- `event_admin_manage_players`: административно управлять заявками, участниками и составами любого мероприятия пространства.
- `event_admin_manage_bracket`: административно менять сетку, стадии, группы, посев и результаты матчей любого мероприятия пространства.
- `event_admin_cancel`: административно отменять любое мероприятие пространства.
- `event_admin_complete`: административно завершать стадии и мероприятия при необходимости ручного вмешательства.

Нельзя перегружать `edit_role_set`, `edit_rating_set` или `create_custom` как права управления мероприятиями. Локальный organizer в Event Service имеет полную власть над своим мероприятием независимо от server permissions. Server permissions нужны только для создания мероприятия и административных override-сценариев над чужими мероприятиями или аварийного восстановления состояния.

## Проверка Restrictions В Event Service
- `server_ban`: запрещать создание, вступление, подачу заявки и любые organizer-действия в мероприятиях этого пространства.
- `mix_ban`: запрещать участие в одиночном матче или mix-событии; organizer-действия можно разрешать только если бизнес-правила допускают неучаствующих организаторов.
- `tournament_ban`: запрещать участие в турнирном событии; organizer-действия можно разрешать только если бизнес-правила допускают неучаствующих организаторов.
- `self_edit_name`: не влияет на Event Service, если Event Service не изменяет nickname участника.

## Open Rating Source
- Open/expert ratings для формирования команд должны приходить из `custom.get_by_member` или из локального event snapshot, если организатор переопределяет рейтинг на мероприятие.
- Перед вызовом балансировщика Event Service вызывает `rating.effective.calculate` из `mixtura_ranker`, если расчет эффективного рейтинга включен.
- Если `rating.effective.calculate` выключен, Event Service использует open rating как расчетный рейтинг для балансировщика и явно сохраняет источник рейтинга в snapshot.
- Event Service должен сохранять исходный open rating, расчетный rating для балансировщика и источник расчета.

## Важные Риски Контракта
- `member.get` возвращает участника по id без server-specific request field, поэтому Gateway должен проверять `server_id` перед передачей участника в Event Service; Event Service дополнительно валидирует `server_id` в полученном payload.
- `role_set.get_by_server` и `rating_set.get_by_server` получают `server_id` из `access_data`; Gateway должен вызывать их и передавать Event Service только нужный для use case payload.
- Если Gateway передает устаревшие masks, Event Service может принять неверное решение. Поэтому masks должны вычисляться на Gateway непосредственно перед RPC-командой.
