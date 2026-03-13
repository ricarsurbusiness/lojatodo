from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class TokenData(BaseSchema):
    user_id: int
    email: str
    roles: List[str]


class MessageResponse(BaseSchema):
    message: str


class ErrorResponse(BaseSchema):
    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    page: int
    limit: int
    total: int
    total_pages: int


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
