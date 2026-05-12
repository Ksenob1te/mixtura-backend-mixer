from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.models.application import ApplicationStatus


class ApplicationRoleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    game_role_id: UUID | None = None
    priority: int


class ApplicationIntegrationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    integration_id: UUID
    provider_id: UUID
    provider_name: str


class ApplicationFilledFieldItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    custom_field_id: UUID
    value: str


class ApplicationRolePriorityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    priority: int


class ApplicationSubmitResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: ApplicationStatus
    auto_approved: bool
    player_id: UUID


class ApplicationReviewResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: ApplicationStatus
    player_id: UUID | None = None


class ApplicationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    member_id: UUID
    status: ApplicationStatus
    role_priorities: list[ApplicationRolePriorityItem] = Field(default_factory=list)
    filled_fields: list[ApplicationFilledFieldItem] = Field(default_factory=list)
    integrations: list[ApplicationIntegrationItem] = Field(default_factory=list)
    event_player_id: UUID | None = None


class ApplicationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    status: ApplicationStatus
    is_approved: bool
    created_at: datetime
    roles: list[ApplicationRoleItem] = Field(default_factory=list)
    integrations: list[ApplicationIntegrationItem] = Field(default_factory=list)
