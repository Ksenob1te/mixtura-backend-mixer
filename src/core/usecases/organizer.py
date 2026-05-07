from src.core.commands.organizer import (
    ListOrganizersCommand,
    AddOrganizerCommand,
    RemoveOrganizerCommand,
)
from src.core.exceptions import BadRequestException, ForbiddenException, NotFoundException, ConflictException
from src.core.models.event import EventStatus
from src.core.models.organizer import OrganizerCreate
from src.core.usecases._access import (
    R_SERVER_BAN,
    P_EVENT_ADMIN_VIEW,
    P_EVENT_ADMIN_MANAGE_ORGANIZERS,
    has_restriction,
    has_permission,
)


class ListOrganizersUseCase:
    def __init__(self, organizer_repo, event_repo):
        self._organizer_repo = organizer_repo
        self._event_repo = event_repo

    async def __call__(self, command: ListOrganizersCommand) -> list[dict]:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data

        if access is not None:
            is_organizer = any(o.member_id == access.member_id for o in event.organizers)
            has_admin_view = has_permission(access.permission_mask, P_EVENT_ADMIN_VIEW)
            if not is_organizer and not has_admin_view:
                if not event.is_public:
                    raise NotFoundException("Event not found")
                raise ForbiddenException("Only organizer or event admin can view organizers")
        elif not event.is_public:
            raise NotFoundException("Event not found")

        organizers = await self._organizer_repo.list_by_event(command.event_id)

        return [
            {"id": str(o.id), "event_id": str(o.event_id), "member_id": str(o.member_id)}
            for o in organizers
        ]


class AddOrganizerUseCase:
    def __init__(self, organizer_repo, event_repo):
        self._organizer_repo = organizer_repo
        self._event_repo = event_repo

    async def __call__(self, command: AddOrganizerCommand) -> dict:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data

        if has_restriction(access.restriction_mask, R_SERVER_BAN):
            raise ForbiddenException("Server ban prevents organizer management")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_permission(access.permission_mask, P_EVENT_ADMIN_MANAGE_ORGANIZERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can manage organizers")

        if event.status == EventStatus.COMPLETED or event.status == EventStatus.CANCELLED:
            raise BadRequestException("Cannot modify organizers of completed or cancelled event")

        existing = await self._organizer_repo.list_by_event(command.event_id)
        if any(o.member_id == command.member_id for o in existing):
            raise ConflictException("Member is already an organizer")

        organizer = await self._organizer_repo.create(
            OrganizerCreate(event_id=command.event_id, member_id=command.member_id)
        )

        return {"id": str(organizer.id), "event_id": str(organizer.event_id), "member_id": str(organizer.member_id)}


class RemoveOrganizerUseCase:
    def __init__(self, organizer_repo, event_repo):
        self._organizer_repo = organizer_repo
        self._event_repo = event_repo

    async def __call__(self, command: RemoveOrganizerCommand) -> None:
        event = await self._event_repo.get(command.event_id, load_organizers=True)
        if not event:
            raise NotFoundException("Event not found")

        access = command.access_data

        if has_restriction(access.restriction_mask, R_SERVER_BAN):
            raise ForbiddenException("Server ban prevents organizer management")

        is_organizer = any(o.member_id == access.member_id for o in event.organizers)
        has_admin = has_permission(access.permission_mask, P_EVENT_ADMIN_MANAGE_ORGANIZERS)

        if not is_organizer and not has_admin:
            raise ForbiddenException("Only organizer or event admin can manage organizers")

        if event.status == EventStatus.COMPLETED or event.status == EventStatus.CANCELLED:
            raise BadRequestException("Cannot modify organizers of completed or cancelled event")

        existing_organizers = await self._organizer_repo.list_by_event(command.event_id)

        if len(existing_organizers) <= 1:
            raise BadRequestException("Cannot remove the last organizer")

        target = next((o for o in existing_organizers if o.member_id == command.member_id), None)
        if not target:
            raise NotFoundException("Member is not an organizer")

        await self._organizer_repo.delete(target.id)
