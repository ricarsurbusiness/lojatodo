from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class DashboardResponse(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: Decimal
    recent_orders: List["OrderSummary"]
    top_products: List["ProductPerformance"]


class OrderSummary(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime


class ProductPerformance(BaseModel):
    product_id: int
    name: str
    quantity_sold: int
    revenue: Decimal


class AdminUserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    roles: Optional[List[str]] = None
    created_at: datetime


class AdminUserListResponse(BaseModel):
    items: List[AdminUserResponse]
    total: int
    page: int
    limit: int
    pages: int


class AdminOrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminOrderListResponse(BaseModel):
    items: List[AdminOrderResponse]
    total: int
    page: int
    limit: int
    pages: int


class UpdateOrderStatusRequest(BaseModel):
    status: str


class UpdateOrderStatusResponse(BaseModel):
    id: int
    status: str
    updated_at: datetime


class ErrorResponse(BaseModel):
    detail: str
    service: Optional[str] = None


DashboardResponse.model_rebuild()
