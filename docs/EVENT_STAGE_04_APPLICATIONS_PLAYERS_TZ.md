# ТЗ Для Агента: Этап 4. Заявки И Участники

## Цель
Реализовать join/application flow и управление участниками мероприятия. После этапа должен работать сценарий: создать событие, открыть регистрацию, подать заявку, принять заявку, получить игрока мероприятия.

## Общий Контекст
- Event Service хранит заявки, ответы на кастомные поля, выбранные интеграции, приоритеты ролей и игроков мероприятия.
- Пользователи, membership, integrations, role set и restrictions приходят через Gateway из Server Service.
- Для большинства команд `access_data.member_id` должен быть не `None`.
- Публичные read-only сценарии могут работать без `access_data`, если возвращают только публичные поля.
- Organizer имеет полную власть над своим event, server permissions нужны только для административных override-сценариев.

## Основные Сущности
- `Application`: заявка участника на мероприятие.
- `ApplicationStatus`: минимум `PENDING`, `APPROVED`, `REJECTED`, `WAITLIST` или согласованный набор enum-значений.
- `ApplicationCustomField`: настройка кастомного поля заявки.
- `FilledApplicationField`: ответ участника на кастомное поле.
- `ApplicationIntegration`: выбранная или подтвержденная интеграция участника.
- `SelectedGameRole`: выбранная роль и priority участника.
- `EventPlayer`: участник мероприятия, создается после auto-join или approve.

## JoinEventUseCase
- Проверить, что событие находится в состоянии, допускающем регистрацию.
- Проверить окно приема заявок и временные ограничения.
- Проверить `access_data.member_id` и соответствие `access_data.server_id` событию.
- Проверить restrictions: `server_ban` запрещает join/application; `mix_ban` запрещает участие в mix/одиночном матче; `tournament_ban` запрещает участие в турнире.
- Проверить обязательные интеграции по payload, переданному Gateway.
- Проверить обязательные кастомные поля.
- Проверить выбранные игровые роли и priorities по role set пространства.
- Проверить уникальность заявки `event_id + member_id`.
- Если `use_application=false`, создать `Application` со статусом `APPROVED` и `EventPlayer`.
- Если `use_application=true`, создать `Application` со статусом `PENDING`.

## ReviewApplicationUseCase
- Доступен organizer или server-admin override `event_admin_manage_players`.
- Поддержать approve, reject, waitlist.
- При approve создать или обновить `EventPlayer`.
- При reject не создавать `EventPlayer`, если он еще не создан.
- При waitlist сохранить статус ожидания без потери заполненных данных.
- Все решения должны сохранять reviewer, timestamp и причину, если такие поля есть или добавляются.

## Player Management
- Получить список заявок с фильтрами по статусу.
- Получить список игроков мероприятия с фильтрами по статусу.
- Поддержать ручное изменение статуса игрока organizer-ом или `event_admin_manage_players`.
- Поддержать исключение игрока из мероприятия, если это не нарушает уже завершенные матчи.
- Нельзя удалить, деактивировать или перевести в несовместимый статус игрока, который участвует в active match, без отдельного admin override/cancel match flow.
- Сохранять приоритеты ролей игрока для этапа формирования команд.

## Валидация
- Нельзя принять заявку на событие из другого `server_id`.
- Нельзя подать повторную заявку тем же `member_id` на тот же `event_id`, если не реализован отдельный flow отзыва/повторной подачи.
- Нельзя сохранять ответы на несуществующие или чужие custom fields.
- Нельзя сохранять роли, отсутствующие в role set события.
- Нельзя принимать заявку для `COMPLETED`/`CANCELLED` event или вне разрешенных registration settings/window. Не требовать отдельного глобального event status `REGISTRATION`.
- Нельзя менять статус игрока так, чтобы сломать активный матч или уже зафиксированный результат.

## RPC
- `event.application.submit`: подать заявку или выполнить auto-join.
- `event.application.get`: получить заявку с заполненными полями, integrations и selected roles.
- `event.application.list`: получить список заявок события с фильтрами по статусу.
- `event.application.review`: approve/reject/waitlist заявки.
- `event.player.list`: получить список игроков мероприятия с фильтрами по статусу.
- `event.player.status.update`: изменить статус игрока organizer/admin-командой с учетом active match restrictions.
- `event.player.remove`: исключить игрока из event, если это не ломает active/completed matches.

## Задачи
- Описать command DTO: `SubmitApplicationCommand`, `ReviewApplicationCommand`, list/get commands.
- Реализовать `JoinEventUseCase`.
- Реализовать `ReviewApplicationUseCase`.
- Реализовать use cases списков заявок и игроков.
- Реализовать репозиторные методы, необходимые для уникальности и загрузки aggregate-графов.
- Подключить use cases к RPC handlers.

## Не Делать
- Не реализовывать формирование команд.
- Не реализовывать сетки и матчи.
- Не вызывать Server Service напрямую для проверки integrations или roles.
- Не синхронизировать Alembic.
- Не писать и не исправлять тесты; тестирование вынесено в этап 10.

## Критерии Приемки
- Работает сценарий `создать событие -> открыть регистрацию -> подать заявку -> принять заявку -> получить EventPlayer`.
- Auto-join без заявок сразу создает approved application и event player.
- Restrictions блокируют участие корректно.
- Organizer может обрабатывать заявки без server permissions.
- Server-admin override может обрабатывать заявки чужого event при наличии `event_admin_manage_players`.

## Команды Проверки
- `uv run mypy src`
