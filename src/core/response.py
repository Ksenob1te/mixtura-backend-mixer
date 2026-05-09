from typing import TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMessage(BaseModel, Generic[T]):
    status: int
    message: T


class ErrorResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: str = Field(default="ok")
