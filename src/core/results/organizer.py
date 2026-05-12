from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    member_id: UUID
