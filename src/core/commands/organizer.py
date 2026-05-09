from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest


class ListOrganizersCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class AddOrganizerCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID


class RemoveOrganizerCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID
