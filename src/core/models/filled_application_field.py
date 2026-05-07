from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .application import Application
    from .application_custom_field import ApplicationCustomField


class FilledApplicationField(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    value: str
    custom_field_id: UUID
    application_id: UUID
    created_at: datetime
    custom_field: Optional[ApplicationCustomField] = None
    application: Optional[Application] = None


class FilledApplicationFieldCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    value: str
    custom_field_id: UUID
    application_id: UUID
