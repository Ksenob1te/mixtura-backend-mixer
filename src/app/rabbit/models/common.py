from uuid import UUID

from pydantic import BaseModel


class AccessDataRequest(BaseModel):
    """Auth block sent with every message — wire contract."""
    model_config = {"extra": "forbid"}

    member_id: UUID | None
    server_id: UUID
    permission_mask: int
    restriction_mask: int


class PaginationRequest(BaseModel):
    """Pagination params — wire contract."""
    model_config = {"extra": "forbid"}

    page: int | None = None
    page_size: int = 50
