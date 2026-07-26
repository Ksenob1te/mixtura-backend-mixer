from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.application import ApplicationStatus

from .common import AccessDataRequest, PaginationRequest


# ── Input message schemas ──────────────────────────────────────────────

class IntegrationPayload(BaseModel):
    integration_id: UUID
    provider_id: UUID
    provider_name: str


class FilledFieldPayload(BaseModel):
    custom_field_id: UUID
    value: str


class RolePriorityPayload(BaseModel):
    role_id: UUID
    priority: int


class SubmitApplicationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    integrations: list[IntegrationPayload] = Field(default_factory=list)
    filled_fields: list[FilledFieldPayload] = Field(default_factory=list)
    role_priorities: list[RolePriorityPayload] = Field(default_factory=list)


class GetApplicationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    application_id: UUID
    access_data: AccessDataRequest


class ReviewApplicationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    application_id: UUID
    status: ApplicationStatus
    role_priorities: list[RolePriorityPayload] = Field(default_factory=list)


class ListApplicationsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
    status: ApplicationStatus | None = None
    pagination: PaginationRequest = PaginationRequest()
    sort_by: str = "created_at"
    sort_order: str = "desc"


# ── Output response schemas ────────────────────────────────────────────

class ApplicationRoleItem(BaseModel):
    role_id: UUID
    game_role_id: UUID | None = None
    priority: int


class ApplicationIntegrationItem(BaseModel):
    integration_id: UUID
    provider_id: UUID
    provider_name: str


class ApplicationFilledFieldItem(BaseModel):
    custom_field_id: UUID
    value: str


class ApplicationRolePriorityItem(BaseModel):
    role_id: UUID
    priority: int


class ApplicationSubmitResult(BaseModel):
    id: UUID
    status: ApplicationStatus
    auto_approved: bool
    player_id: UUID


class ApplicationReviewResult(BaseModel):
    id: UUID
    status: ApplicationStatus
    player_id: UUID | None = None


class ApplicationDetailResponse(BaseModel):
    id: UUID
    event_id: UUID
    member_id: UUID
    status: ApplicationStatus
    role_priorities: list[ApplicationRolePriorityItem] = Field(default_factory=list)
    filled_fields: list[ApplicationFilledFieldItem] = Field(default_factory=list)
    integrations: list[ApplicationIntegrationItem] = Field(default_factory=list)
    event_player_id: UUID | None = None


class ApplicationListItem(BaseModel):
    id: UUID
    member_id: UUID
    status: ApplicationStatus
    created_at: datetime
    roles: list[ApplicationRoleItem] = Field(default_factory=list)
    integrations: list[ApplicationIntegrationItem] = Field(default_factory=list)
