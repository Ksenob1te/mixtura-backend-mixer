from uuid import UUID

from pydantic import BaseModel

from .common import AccessDataRequest, PaginationRequest


class ListOrganizersMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    pagination: PaginationRequest = PaginationRequest()


class AddOrganizerMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID


class RemoveOrganizerMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    member_id: UUID


class OrganizerItem(BaseModel):
    id: UUID
    event_id: UUID
    member_id: UUID
