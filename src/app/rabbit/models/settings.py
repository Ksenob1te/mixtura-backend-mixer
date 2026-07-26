from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .common import AccessDataRequest


class AddIntegrationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    provider_id: UUID


class RemoveIntegrationMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    integration_id: UUID


class AddGameRoleMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    game_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class UpdateGameRoleMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    selected_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class RemoveGameRoleMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    selected_role_id: UUID


class AddCustomFieldMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    name: str
    is_private: bool = False
    is_required: bool = False


class UpdateCustomFieldMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    field_id: UUID
    name: str | None = None
    is_private: bool | None = None
    is_required: bool | None = None


class RemoveCustomFieldMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    field_id: UUID


class UpdateTimeSettingsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    access_data: AccessDataRequest
    event_id: UUID
    start_time: datetime | None = None
    end_time: datetime | None = None


class GetApplicationFormSettingsMessage(BaseModel):
    model_config = {"extra": "forbid"}
    event_id: UUID
    access_data: AccessDataRequest
