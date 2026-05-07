> Legacy/reference document. Для реализации Event Service source of truth: `EVENT_MODULE_IMPLEMENTATION_PLAN.md`, `EVENT_STAGE_*_TZ.md`, `SERVER_GATEWAY_EVENT_INTEGRATION.md`, `EXTERNAL_BALANCER_RANKER_INTEGRATION.md`.

﻿# Исчерпывающая Архитектура: REST API, Сервисы и Юзкейсы 
(Единая платформа Event: Турниры и Миксы)
Данный документ содержит максимально расширенный и детализированный перечень всех возможных REST API эндпоинтов, CRUD-операций, специализированных бизнес-методов внутри доменных сервисов и оркеструющих юзкейсов. Включены как базовые, так и теоретически необходимые методы для полноценной работы крупной платформы (массовые операции, статистика, модерация, отмена действий).

Несмотря на то, что описаны REST эндпоинты, данный сервис коммуницирует с другими сервисами через RPC over RabbitMQ с помощью библиотеки faststream. В свою очередь этот сервис должен обеспечить нужный функционал для данных эндпоинтов в Gateway.
---
## 1. Уровень REST API (Внешние эндпоинты)
### 1.1. Управление Мероприятием (Event & Organizer)
- **POST /events** — Создать мероприятие.
- **GET /events** — Список мероприятий (пагинация, фильтры: статус, тип, даты, теги).
- **GET /events/{id}** — Полная карточка мероприятия.
- **PUT /events/{id}** — Редактировать основные данные (название, описание, обложка).
- **PATCH /events/{id}/status** — Сменить статус сессии (Draft -> Published -> Registration -> Check-in -> Live -> Finished -> Archived).
- **POST /events/{id}/clone** — Склонировать настройки текущего мероприятия в новое (удобно для регулярных турниров).
- **DELETE /events/{id}** — Мягкое удаление (soft delete) / отмена мероприятия.
- **GET /events/{id}/organizers** — Список организаторов и их прав.
- **POST /events/{id}/organizers** — Добавить организатора/судью.
- **PATCH /events/{id}/organizers/{user_id}** — Изменить уровень прав организатора.
- **DELETE /events/{id}/organizers/{user_id}** — Удалить организатора.
- **GET /events/{id}/statistics** — Сводная статистика (сколько регистраций, матчей, активных игроков).
### 1.2. Конфигурация формы заявок и требований (Application Config)
- **GET /events/{id}/config** — Получить всю конфигурацию регистрации разом.
- **POST /events/{id}/config/fields** — Добавить новое кастомное поле (ApplicationCustomField).
- **PUT /events/{id}/config/fields/{field_id}** — Обновить настройки поля (сделать обязательным, изменить тип).
- **DELETE /events/{id}/config/fields/{field_id}** — Удалить поле из формы.
- **POST /events/{id}/config/integrations** — Добавить требование привязки (Steam, Discord).
- **DELETE /events/{id}/config/integrations/{req_id}** — Убрать требование интеграции.
- **POST /events/{id}/config/time-settings** — Создать временной слот лимитов (ApplicationTimeSettings).
- **PUT /events/{id}/config/time-settings/{slot_id}** — Обновить квоты по времени.
- **DELETE /events/{id}/config/time-settings/{slot_id}** — Удалить слот.
- **PUT /events/{id}/config/roles** — Перезаписать список доступных позиций (PlayerRole) для выбора на турнире.
### 1.3. Обработка Заявок (Applications Flow)
- **POST /events/{id}/applications** — Разместить заявку пользователем (в т.ч. FilledApplicationField, проверки ApplicationIntegration).
- **GET /events/{id}/applications** — Список заявок (фильтры: Approved, Pending, Rejected).
- **GET /events/{id}/applications/export** — Экспорт списка заявок (CSV/Excel) для админов.
- **GET /applications/{app_id}** — Детальный просмотр заявки с ответами пользователя.
- **PATCH /applications/{app_id}/status** — Изменить статус заявки (Approve / Reject / Request Changes).
- **POST /events/{id}/applications/bulk-approve** — Массовое одобрение выделенных заявок.
- **POST /events/{id}/applications/bulk-reject** — Массовое отклонение заявок (с общей причиной).
- **DELETE /applications/{app_id}** — Отзыв заявки самим пользователем.
### 1.4. Пулы игроков, Check-in и Наблюдатели (EventPlayer & Mixer Pools)
- **POST /events/{id}/check-in** — Чек-ин пользователя (переводит Approved заявку в EventPlayer).
- **DELETE /events/{id}/check-in** — Отмена чек-ина пользователем до старта.
- **GET /events/{id}/players** — Список участников текущего турнира/микса (с указанием принадлежности к команде или пулу).
- **PATCH /events/{id}/players/{player_id}/roles** — Игрок корректирует предпочтительные роли (SelectedGameRole).
- **PATCH /events/{id}/players/{player_id}/pool-status** — Игрок меняет статус пула (Waitlist <-> Active).
- **POST /events/{id}/players/{player_id}/force-status** — Админ переводит игрока в Active/Waitlist принудительно.
- **DELETE /events/{id}/players/{player_id}** — Кик/дисквалификация участника (бан на текущем Event).
### 1.5. Команды и Составы (Teams & Roster)
- **POST /events/{id}/teams** — Создать команду (название, лого).
- **GET /events/{id}/teams** — Список всех команд события.
- **GET /teams/{team_id}** — Профиль команды и её ростер (TeamPlayer).
- **PUT /teams/{team_id}** — Изменить профиль команды (название).
- **POST /teams/{team_id}/players** — Пригласить / добавить EventPlayer в команду.
- **PATCH /teams/{team_id}/players/{player_id}/role** — Назначить игроку внутрикомандную роль (капитан, стендин).
- **POST /teams/{team_id}/transfer-captain** — Передать лидерство другому игроку.
- **DELETE /teams/{team_id}/players/{player_id}** — Кик игрока из команды (капитаном).
- **POST /teams/{team_id}/leave** — Покинуть команду самостоятельно.
- **DELETE /teams/{team_id}** — Распустить команду.
### 1.6. Фазы, Сетки и Группы (Stages & Brackets)
- **POST /events/{id}/stages** — Создать новую стадию (Stage - Группы, Плей-офф, Швейцарка).
- **GET /events/{id}/stages** — Порядок и настройки стадий турнира.
- **PUT /stages/{stage_id}** — Редактировать настройки стадии (RoundRobinSettings / SwissSettings).
- **DELETE /stages/{stage_id}** — Удалить стадию вместе с матчами (опасная зона).
- **POST /stages/{stage_id}/generate** — Сгенерировать сетку (Bracket) / группы (StageGroup) на основе списка команд/игроков.
- **POST /stages/{stage_id}/reseed** — Перемешать (re-seed) участников перед стартом стадии.
- **GET /stages/{stage_id}/bracket** — Получить визуальное дерево (BracketPlacement) с текущим состоянием.
- **GET /stages/{stage_id}/standings** — Получить турнирную таблицу (лидерборд, подсчет очков для групп/Swiss).
- **POST /stages/{stage_id}/advance-round** — Вручную инициировать старт следующего тура (особенно актуально для Swiss).
### 1.7. Матчи, Судейство и Конфликты (Matches & Scores)
- **GET /matches** — Глобальный список матчей (с фильтрами по этапам, статусу Live/Finished).
- **GET /matches/{match_id}** — Детальная инфа (включая MatchSlot, историю изменений счета).
- **PATCH /matches/{match_id}/schedule** — Сдвинуть время/дату игры.
- **PATCH /matches/{match_id}/slots/swap** — Поменять местами участников (Home/Away).
- **PATCH /matches/{match_id}/slots/{slot_id}** — Принудительная замена команды/игрока в слоте матча.
- **POST /matches/{match_id}/score/report** — Команда/игрок отправляет результаты (MatchScore).
- **POST /matches/{match_id}/score/confirm** — Подтверждение результата оппонентом (авто-завершение матча).
- **POST /matches/{match_id}/score/dispute** — Оппонент поднимает флаг конфликта (Conflict State).
- **POST /matches/{match_id}/score/resolve** — Админ разрешает конфликт, принудительно задавая верный MatchScore.
- **POST /matches/{match_id}/forfeit** — Присудить техническое поражение (Walkover) одной из сторон (дисквал за неявку).
- **POST /matches/{match_id}/undo** — Откатить матч к состоянию "Не сыгран" (сброс очков, откат в сетке BracketPlacement).
### 1.8. Модуль Драфта (Draft MixCup)
- **POST /events/{id}/drafts** — Создать конфигурацию драфта (кол-во раундов, время на пик, капитаны).
- **GET /drafts/{draft_id}** — Текущий статус: чей ход, доступный пул, уже задрафтованные (DraftedPlayer).
- **POST /drafts/{draft_id}/start** — Запустить таймер драфта.
- **POST /drafts/{draft_id}/pause** — Приостановить таймер (администратор).
- **POST /drafts/{draft_id}/pick** — Капитан выбирает участника.
- **POST /drafts/{draft_id}/skip** — Пропуск пика капитаном.
- **POST /drafts/{draft_id}/reset** — Полный сброс результатов драфта.
- **POST /drafts/{draft_id}/finalize** — Завершение сессии и авто-превращение DraftedPlayer в Teams & TeamPlayers.
---
## 2. Внутренние Доменные Сервисы (Domain Services)
Слой абстракции над ORM, отвечающий за базовую логику конкретной предметной области. Строго изолированы друг от друга.
### 2.1. EventService & OrganizerService
**Базовые:** create(), get_by_id(), update(), delete()
**Специфичные:** 
- publish_event(), archive_event()
- clone_configurations(source_id, dest_id)
- add_organizer(), remove_organizer(), update_permissions()
- validate_organizer_access(user_id, event_id, action)
### 2.2. ApplicationConfigService
**Базовые:** CRUD для ApplicationCustomField, RequiredIntegration, ApplicationTimeSettings
**Специфичные:**
- reorder_custom_fields(event_id, new_order_list)
- check_available_time_slots(event_id, timestamp)
- validate_user_integrations(user_id, event_id)
### 2.3. ApplicationService
**Базовые:** create_app(), get_app_by_id(), update_app_status()
**Специфичные:**
- ingest_filled_fields(app_id, fields_data)
- bulk_update_status(app_ids_list, new_status, reason)
- verify_application_completeness(app_id)
- count_pending_applications(event_id)
### 2.4. ParticipantPoolService (Управление игроками и Mix-пулом)
**Базовые:** create_event_player(), 
emove_event_player(), get_player_by_id()
**Специфичные:**
- transition_pool_status(player_id, from_status, to_status) (отвечает за State-Lock)
- get_eligible_mix_players(event_id, role_requirements)
- increment_matches_played(player_id)
- update_last_active_timestamp(player_id)
- bulk_set_watchers_status(player_ids_list) (групповой возврат в пул после микс-игры)
- kick_and_ban_player(player_id)
### 2.5. TeamManagementService
**Базовые:** create_team(), update_team(), delete_team()
**Специфичные:**
- add_team_member(team_id, player_id, is_captain)
- remove_team_member(team_id, player_id)
- transfer_captaincy(team_id, old_cap_id, new_cap_id)
- verify_team_readiness(team_id, min_players, max_players)
- bulk_create_teams_from_draft(draft_result_mapping)
### 2.6. TournamentStageService & BracketService
**Базовые:** create_stage(), update_stage(), delete_stage()
**Специфичные:**
- bind_ruleset(stage_id, ruleset_orm_object) (привязка швейцарки или RR).
- generate_empty_bracket_tree(stage_id, participant_count)
- seed_participants_into_bracket(stage_id, ordered_participant_list)
- generate_round_robin_groups(stage_id, participants_list, group_count)
- calculate_stage_standings(stage_id) (высчитывание очков, разницы раундов).
- find_next_bracket_node(current_placement_id, is_winner_path)
### 2.7. MatchService
**Базовые:** create_match(), get_match(), update_match_time()
**Специфичные:**
- assign_slot(match_id, slot_index, participant_id)
- submit_score_proposal(match_id, reporter_id, score_data)
- mark_as_conflict(match_id)
- finalize_match_result(match_id, final_score_data)
- apply_forfeit(match_id, losing_participant_id)
- rollback_match_state(match_id)
- is_match_locked(match_id)
### 2.8. DraftService
**Базовые:** create_draft_session(), get_session_state()
**Специфичные:**
- register_pick(draft_id, picker_id, target_player_id)
- execute_auto_pick(draft_id) (если кончилось время)
- skip_turn(draft_id)
- get_available_draft_pool(draft_id)
---
## 3. Оркеструющие Юзкейсы (Application Services / Use Cases)
Слой, реализующий транзакционные бизнес-процессы (Business Flows), в которых участвуют несколько доменных сервисов (распределенные логические транзакции).
### 3.1. Флоу регистрации (Application Submission Flow)
**Действия:**
1. Запрос ApplicationConfigService на валидацию временных слотов.
2. Вызов интеграционных чеков (проверка привязки Steam/Discord к аккаунту).
3. Валидация кастомных полей на соответствие схеме эвента.
4. Вызов ApplicationService для сохранения заявки.
*(Бонус: отправка Email/Push-уведомления организатору о новой заявке).*
### 3.2. Чек-ин пользователя (Check-in & Event Onboarding)
**Действия:**
1. Проверка в ApplicationService (Статус заявки == Approved).
2. Вызов ParticipantPoolService: создание EventPlayer (статус = Waitlist).
3. Парсинг SelectedGameRole из данных формы заявки и привязка к игроку.
4. Если режим турнира командный — поиск или автоматическое создание Team через TeamManagementService.
### 3.3. Разрешение конфликта модератором (Conflict Resolution Flow)
**Действия:**
1. Проверка прав администратора через OrganizerService.
2. Вызов MatchService.finalize_match_result() с переданными админом цифрами.
3. Вызов AdvanceTournamentMatchUseCase с подтвержденным победителем для продвижения по турнирной сетке (если это турнир) ИЛИ CompleteMixerMatchUseCase (если это микс-игра).
### 3.4. Завершение матча в Миксе (Mixer Post-Match & Unlock Flow)
**Действия:**
1. MatchService финализирует счет.
2. ParticipantPoolService инкрементирует played_matches_count всем участникам матча.
3. **State Lock Release:** ParticipantPoolService меняет статус участников в MatchSlot со "State: Playing" обратно на "State: Waitlist".
4. Обновление таймстемпа выхода в пул (last_active_timestamp), чтобы алгоритм балансировки ставил их в конец очереди.
### 3.5. Алгоритм Балансировки Микса (Matchmaking Generation Engine)
**Действия:**
1. Извлечение параметров матча (сколько слотов, какие роли).
2. Исключение игроков со "State Lock" (уже играют) через ParticipantPoolService.
3. Получение доступного пула "Active".
4. *Пайплайн сортировки*:
   - Primary: Минимальное количество сыгранных матчей.
   - Secondary: Наибольшее время ожидания с момента чек-ина или последней игры.
5. Фильтрация по совпадению ролей (SelectedGameRole).
6. Генерация матча в MatchService.
7. Развешивание "State Lock" (перевод выбранных в Playing статус).
8. (Опционально) Уведомление через Websocket о найденном матче.
### 3.6. Генерация гибридной стадии турнира (Hybrid Stage Generation Flow)
**Действия:**
1. Проверка TeamManagementService / ParticipantPoolService на готовность всех участников (нет неподтвержденных).
2. Чтение настроек фазы из TournamentStageService.
3. **Кейс А (RR / Группы):** Разделение на StageGroup рандомом или по сиду. Создание Match формата каждый с каждым.
4. **Кейс Б (Swiss):** Оценка текущего Standings (очков), спаривание участников с равным кол-вом побед, генерация Match.
5. **Кейс В (Elimination):** Создание всех узлов дерева BracketPlacement, проброс команд в раунд 1.
### 3.7. Движение победителей по сетке (Routing & Ladder Advance Flow)
**Действия:**
1. Срабатывает по хуку (венту) MatchFinalized.
2. TournamentStageService определяет BracketPlacement завершившегося матча.
3. Идентификация Winner и Loser слотов.
4. Транзакции для **Winner**:
   - Поиск узла "следующий матч победителя".
   - Вызов MatchService.assign_slot() для будущего матча.
5. Транзакции для **Loser**:
   - Если Single Elimination -> помечается как Eliminated.
   - Если Double Elimination -> поиск маршрута в сетку лузеров, MatchService.assign_slot().
### 3.8. Перевод Драфта в Команды (Finalize Draft & Convert to Tournament)
**Действия:**
1. Проверка DraftService (все раунды завершены).
2. Транзакционный маппинг: для каждого Капитана создается Team в TeamManagementService.
3. Все DraftedPlayer, выбранные этим капитаном, автоматически становятся TeamPlayer.
4. (Опционально) Удаление из турнира невыбранных игроков (перевод в Spectator) или генерация для них "Остаточной" команды.
