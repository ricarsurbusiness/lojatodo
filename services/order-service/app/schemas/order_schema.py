from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.order_model import OrderStatus


class ShippingAddress(BaseModel):
    street: str = Field(..., min_length=3)
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)
    zip_code: str = Field(..., min_length=4)
    country: str = Field(..., min_length=2)


class OrderCreateItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class OrderCreateRequest(BaseModel):
    items: List[OrderCreateItem] = Field(..., min_length=1)
    shipping_address: ShippingAddress
    payment_provider: str = Field(default="stripe")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime


class OrderDetailResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    shipping_address: ShippingAddress
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: List[OrderSummaryResponse]
    total: int
    page: int
    pages: int


class CancelOrderResponse(BaseModel):
    id: int
    status: OrderStatus
    updated_at: datetime


class ShipOrderRequest(BaseModel):
    tracking_number: str = Field(..., min_length=5)
    carrier: str = Field(..., min_length=2)
    estimated_delivery: datetime


class ShipOrderResponse(BaseModel):
    id: int
    status: OrderStatus
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    updated_at: datetime
