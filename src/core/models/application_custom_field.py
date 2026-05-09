from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .event import Event


class ApplicationCustomField(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    name: str
    is_private: bool
    is_required: bool
    event: Optional[Event] = None


class ApplicationCustomFieldCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    name: str
    is_private: bool = False
    is_required: bool = False


class ApplicationCustomFieldUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    name: str | None = None
    is_private: bool | None = None
    is_required: bool | None = None
