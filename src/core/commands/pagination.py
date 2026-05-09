from pydantic import BaseModel


class PaginationRequest(BaseModel):
    page: int | None = None
    page_size: int = 50
