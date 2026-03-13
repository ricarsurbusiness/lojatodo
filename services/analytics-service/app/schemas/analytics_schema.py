from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class DailySales(BaseModel):
    date: str
    revenue: Decimal
    orders_count: int


class SalesMetricsResponse(BaseModel):
    total_revenue: Decimal
    today_revenue: Decimal
    week_revenue: Decimal
    month_revenue: Decimal
    total_orders: int
    period_details: List[DailySales]


class OrderStatusCount(BaseModel):
    status: str
    count: int


class PeriodTrend(BaseModel):
    period: str
    orders_count: int
    revenue: Decimal


class OrderMetricsResponse(BaseModel):
    total_orders: int
    by_status: Dict[str, int]
    by_status_percent: Dict[str, float]
    trends: List[PeriodTrend]


class ProductPerformance(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: Decimal


class ProductMetricsResponse(BaseModel):
    top_products: List[ProductPerformance]
    total_products_sold: int


class UserMetricsResponse(BaseModel):
    total_users: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    active_users: int


class EventOrderCreated(BaseModel):
    event_type: str = "ORDER_CREATED"
    order_id: int
    user_id: int
    user_email: str
    items: List[Dict[str, Any]]
    total_amount: Decimal
    created_at: datetime


class EventPaymentCompleted(BaseModel):
    event_type: str = "PAYMENT_COMPLETED"
    payment_id: int
    order_id: int
    amount: Decimal
    transaction_id: str
    completed_at: datetime
