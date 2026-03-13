from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: int
    quantity: int
    reserved_quantity: int
    available_quantity: int


class InventoryCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)


class ReserveRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    order_id: int


class ReserveResponse(BaseModel):
    reservation_id: int
    product_id: int
    quantity: int
    expires_at: datetime


class ConfirmRequest(BaseModel):
    reservation_id: int


class ConfirmResponse(BaseModel):
    reservation_id: int
    status: str
    message: str


class ReleaseRequest(BaseModel):
    reservation_id: int


class ReleaseResponse(BaseModel):
    reservation_id: int
    status: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    available_quantity: Optional[int] = None
