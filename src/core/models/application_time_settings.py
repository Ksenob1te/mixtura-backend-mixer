from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .event import Event


class ApplicationTimeSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event: Optional[Event] = None
