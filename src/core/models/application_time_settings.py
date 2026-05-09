from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .event import Event


class ApplicationTimeSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event: Optional[Event] = None


class ApplicationTimeSettingsCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    event_id: UUID
    start_time: datetime | None = None
    end_time: datetime | None = None


class ApplicationTimeSettingsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    start_time: datetime | None = None
    end_time: datetime | None = None
