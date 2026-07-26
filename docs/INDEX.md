# Mixer Service — Documentation Index

> **INSTRUCTION FOR AGENTS:** При внесении изменений в код ОБЯЗАТЕЛЬНО обновляйте соответствующие файлы документации.
>
> **NOTE FOR AGENTS:** Структура и содержание файлов документации описаны в [guides/structure.md](guides/structure.md). Перед созданием нового файла или редактированием существующего — ознакомьтесь с ней.
>
> | Изменение в коде | Что обновить |
> |------------------|--------------|
> | Новый/изменённый handler (`src/app/rabbit/api/<feature>.py`) | `docs/modules/<feature>/api.md` — очереди, команды, результаты |
> | Новый/изменённый метод сервиса (`src/core/services/<feature>.py`) | `docs/modules/<feature>/service.md` — алгоритм, исключения, зависимости |
> | Новая/изменённая команда (`src/core/commands/<feature>.py`) | `docs/modules/<feature>/api.md` — схема Command |
> | Новый/изменённый результат (`src/core/results/<feature>.py`) | `docs/modules/<feature>/api.md` — схема Result |
> | Новая/изменённая модель app-слоя (`src/app/rabbit/models/<feature>.py`) | `docs/modules/<feature>/api.md` — внешняя схема сообщения |
> | Новая/изменённая модель (`src/core/models/<model>.py`) | `docs/models/<model>.md` — поля, роль, связи |
> | Изменение общих схем (AccessDataRequest, ResponseMessage, enums, permissions) | `docs/_shared/<file>.md` |
> | Новый/изменённый репозиторий (`src/core/interfaces/repo/<feature>.py`) | `docs/repositories/<feature>.md` — методы, eager loading |
> | Новый сервис | Создать `docs/modules/<feature>/api.md` + `docs/modules/<feature>/service.md`, добавить в таблицу ниже |
> | Удаление сервиса/метода | Удалить из соответствующих `.md` файлов |

## Modules

| Module | API Contracts | Service Logic |
|--------|--------------|---------------|
| [Event](modules/event/api.md) | [api.md](modules/event/api.md) | [service.md](modules/event/service.md) |
| [Application](modules/application/api.md) | [api.md](modules/application/api.md) | [service.md](modules/application/service.md) |
| [Organizer](modules/organizer/api.md) | [api.md](modules/organizer/api.md) | [service.md](modules/organizer/service.md) |
| [Player](modules/player/api.md) | [api.md](modules/player/api.md) | [service.md](modules/player/service.md) |
| [Draft](modules/draft/api.md) | [api.md](modules/draft/api.md) | [service.md](modules/draft/service.md) |
| [Team](modules/team/api.md) | [api.md](modules/team/api.md) | [service.md](modules/team/service.md) |
| [Team Formation](modules/team-formation/api.md) | [api.md](modules/team-formation/api.md) | [service.md](modules/team-formation/service.md) |
| Balancer Result | — | [service.md](modules/team-formation/service.md#method-complete_formationtask_id-uuid-raw_variants-listdict---none) |
| [Match](modules/match/api.md) | [api.md](modules/match/api.md) | [service.md](modules/match/service.md) |
| [Settings](modules/settings/api.md) | [api.md](modules/settings/api.md) | [service.md](modules/settings/service.md) |
| [Health](modules/health/api.md) | [api.md](modules/health/api.md) | — |

## Status Machines

> Подробные диаграммы переходов, триггеры, условия и guard-проверки для каждого статуса.

| Status | File | Brief |
|--------|------|-------|
| Index | [statuses/INDEX.md](statuses/INDEX.md) | Обзор всех статусных машин и их взаимодействий |
| EventStatus | [statuses/event-status.md](statuses/event-status.md) | Формальная машина состояний: 7 статусов, все переходы через `transition_to()` |
| EventPlayerStatus | [statuses/event-player-status.md](statuses/event-player-status.md) | Жизненный цикл игрока: REGISTERED → SELECTED → PLAYING → COMPLETED |
| ApplicationStatus | [statuses/application-status.md](statuses/application-status.md) | Заявки: PENDING → APPROVED / REJECTED / WAITLIST |
| DraftStatus | [statuses/draft-status.md](statuses/draft-status.md) | Draft-сессия: OPEN → BALANCE_REQUESTED → BALANCE_SELECTED |

## Shared Components

| Component | File | Brief |
|-----------|------|-------|
| AccessDataRequest | [_shared/access-data.md](_shared/access-data.md) | Блок авторизации: member_id, server_id, permission_mask, restriction_mask |
| PaginationRequest | [_shared/pagination.md](_shared/pagination.md) | Стандартная пагинация: page (1-indexed), page_size (default 50) |
| Domain Exceptions | [_shared/domain-exceptions.md](_shared/domain-exceptions.md) | NotFoundException(404), ForbiddenException(403), BadRequestException(400), ConflictException(409), InternalLogicException(500) |
| Response Wrapper | [_shared/response-wrapper.md](_shared/response-wrapper.md) | ResponseMessage\<T\>, ErrorResponse, StatusResponse |
| StatusResponse | [_shared/status-response.md](_shared/status-response.md) | Универсальный ответ: `{"status": "ok"}`, используется organizer.remove, player.remove, health |
| EventDetail / EventCard | [_shared/event-detail.md](_shared/event-detail.md) | Выходные схемы события: EventDetail (15 полей) + EventCard + вложенные типы |
| SingleMatchView | [_shared/single-match-view.md](_shared/single-match-view.md) | Выходная схема матча: SingleMatchView + SingleMatchSlotView |
| Enums | [_shared/enums.md](_shared/enums.md) | EventMatchType, EventStatus, TeamFormation, ApplicationStatus, EventPlayerStatus, DraftStatus, StageFormat, MatchSlotSourceType, BracketPosition |
| Permission Bits | [_shared/permission-bits.md](_shared/permission-bits.md) | P_EVENT_* (bits 24-31), R_MIX_BAN, R_TOURNAMENT_BAN, helper functions |

## Domain Models

| Model | File | Brief |
|-------|------|-------|
| Event | [models/event.md](models/event.md) | Центральная сущность: настройки, статус, связи с командами, draft, players |
| EventPlayer | [models/event-player.md](models/event-player.md) | Участник события: статус, роли, связь с application |
| Application | [models/application.md](models/application.md) | Заявка на участие: статус, integrations, filled fields |
| Team | [models/team.md](models/team.md) | Команда в событии: связь с draft, players |
| TeamPlayer | [models/team-player.md](models/team-player.md) | Член команды: game_role, rating |
| Draft | [models/draft.md](models/draft.md) | Draft-сессия: статус, drafted players |
| DraftedPlayer | [models/drafted-player.md](models/drafted-player.md) | Связь draft → event player |
| Match | [models/match.md](models/match.md) | Матч: времена, раунд, slots, result snapshot |
| MatchSlot | [models/match-slot.md](models/match-slot.md) | Слот матча: source type, team assignment |
| MatchScore | [models/match-score.md](models/match-score.md) | Счёт команды в слоте |
| Bracket | [models/bracket.md](models/bracket.md) | Турнирная сетка события |
| Stage | [models/stage.md](models/stage.md) | Этап турнира: формат, группы |
| StageGroup | [models/stage-group.md](models/stage-group.md) | Группа внутри этапа |
| Organizer | [models/organizer.md](models/organizer.md) | Организатор события (member_id) |
| PlayerRole | [models/player-role.md](models/player-role.md) | Роль игрока в событии: game_role_id, priority |
| SelectedGameRole | [models/selected-game-role.md](models/selected-game-role.md) | Играющая роль, выбранная для события |
| ApplicationCustomField | [models/application-custom-field.md](models/application-custom-field.md) | Кастомное поле формы заявки |
| ApplicationIntegration | [models/application-integration.md](models/application-integration.md) | Интеграция, привязанная к заявке |
| ApplicationTimeSettings | [models/application-time-settings.md](models/application-time-settings.md) | Временные окна регистрации |
| FilledApplicationField | [models/filled-application-field.md](models/filled-application-field.md) | Заполненное поле заявки |
| RequiredIntegration | [models/required-integration.md](models/required-integration.md) | Обязательная интеграция для события |
| SwissSettings | [models/swiss-settings.md](models/swiss-settings.md) | Настройки швейцарской системы |
| RoundRobinSettings | [models/round-robin-settings.md](models/round-robin-settings.md) | Настройки round robin |
| BracketPlacement | [models/bracket-placement.md](models/bracket-placement.md) | Позиция команды в bracket |
| Rating | [models/rating.md](models/rating.md) | DTO-модели для клиента расчёта рейтингов |
| Balancer | [models/balancer.md](models/balancer.md) | DTO-модели для запросов/ответов внешних балансеров |

## Repositories

> **Note for agents:** Новые репозитории должны наследоваться от `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]`. Описывайте только кастомные методы и eager loading флаги — базовые CRUD методы уже задокументированы в [base.md](repositories/base.md).

| Repository | File | Brief |
|------------|------|-------|
| BaseRepository | [repositories/base.md](repositories/base.md) | Generic CRUD, DTO mapping, integrity error handling |
| EventRepository | [repositories/event.md](repositories/event.md) | CRUD + status transitions, 10 eager-load flags |
| ApplicationRepository | [repositories/application.md](repositories/application.md) | CRUD + event/member lookup, status filtering, sorting |
| OrganizerRepository | [repositories/organizer.md](repositories/organizer.md) | CRUD + list by event |
| PlayerRepository | [repositories/player.md](repositories/player.md) | CRUD + event/member lookup, status filtering, roles eager load |
| DraftRepository | [repositories/draft.md](repositories/draft.md) | CRUD + list by event |
| TeamRepository | [repositories/team.md](repositories/team.md) | CRUD + list by event |
| TeamPlayerRepository | [repositories/team_player.md](repositories/team_player.md) | CRUD + list by team |
| MatchRepository | [repositories/match.md](repositories/match.md) | CRUD + stage group queries, active team/draft tracking, event context |
| MatchSlotRepository | [repositories/match_slot.md](repositories/match_slot.md) | CRUD + list by match |
| MatchScoreRepository | [repositories/match_score.md](repositories/match_score.md) | CRUD + lookup by slot |
| BracketRepository | [repositories/bracket.md](repositories/bracket.md) | CRUD + list by event |
| BracketPlacementRepository | [repositories/bracket_placement.md](repositories/bracket_placement.md) | CRUD + list by bracket |
| StageRepository | [repositories/stage.md](repositories/stage.md) | CRUD + list by bracket |
| StageGroupRepository | [repositories/stage_group.md](repositories/stage_group.md) | CRUD + list by stage |
| DraftedPlayerRepository | [repositories/drafted_player.md](repositories/drafted_player.md) | CRUD + list by draft |
| PlayerRoleRepository | [repositories/player_role.md](repositories/player_role.md) | CRUD + list by player |
| SelectedGameRoleRepository | [repositories/selected_game_role.md](repositories/selected_game_role.md) | CRUD + list by event |
| ApplicationCustomFieldRepository | [repositories/application_custom_field.md](repositories/application_custom_field.md) | CRUD + list by event |
| ApplicationIntegrationRepository | [repositories/application_integration.md](repositories/application_integration.md) | CRUD + list by application |
| ApplicationTimeSettingsRepository | [repositories/application_time_settings.md](repositories/application_time_settings.md) | CRUD + get/delete by event |
| FilledApplicationFieldRepository | [repositories/filled_application_field.md](repositories/filled_application_field.md) | CRUD + list by application |
| RequiredIntegrationRepository | [repositories/required_integration.md](repositories/required_integration.md) | CRUD + list by event |
| SwissSettingsRepository | [repositories/swiss_settings.md](repositories/swiss_settings.md) | CRUD + get/delete by stage |
| RoundRobinSettingsRepository | [repositories/round_robin_settings.md](repositories/round_robin_settings.md) | CRUD + get/delete by stage |
| BalancerTaskStore | [repositories/balancer_task.md](repositories/balancer_task.md) | Redis: save/get/delete контекста задач балансировки |
| TeamFormationVariantStore | [repositories/team_formation_variant.md](repositories/team_formation_variant.md) | Redis: save/get/delete вариантов с latest-pointer |
| BalancerRequestRepository | [repositories/balancer_request.md](repositories/balancer_request.md) | RabbitMQ publish: запросы балансировки mix/tournament |
| RatingClient | [repositories/rating.md](repositories/rating.md) | RabbitMQ RPC + publish: effective ratings, match result (typed DTOs) |
