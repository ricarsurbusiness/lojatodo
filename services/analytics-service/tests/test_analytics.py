import pytest
from decimal import Decimal
from datetime import datetime, date

from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schema import (
    SalesMetricsResponse,
    OrderMetricsResponse,
    ProductMetricsResponse,
    UserMetricsResponse
)


@pytest.fixture
def mock_db():
    pass


@pytest.fixture
def mock_redis():
    pass


@pytest.mark.asyncio
async def test_sales_metrics_response():
    response = SalesMetricsResponse(
        total_revenue=Decimal("10000.00"),
        today_revenue=Decimal("500.00"),
        week_revenue=Decimal("3000.00"),
        month_revenue=Decimal("8000.00"),
        total_orders=100,
        period_details=[]
    )
    assert response.total_revenue == Decimal("10000.00")
    assert response.total_orders == 100


@pytest.mark.asyncio
async def test_order_metrics_response():
    response = OrderMetricsResponse(
        total_orders=50,
        by_status={"pending": 10, "completed": 30, "cancelled": 10},
        by_status_percent={"pending": 20.0, "completed": 60.0, "cancelled": 20.0},
        trends=[]
    )
    assert response.total_orders == 50
    assert sum(response.by_status.values()) == 50


@pytest.mark.asyncio
async def test_product_metrics_response():
    response = ProductMetricsResponse(
        top_products=[],
        total_products_sold=0
    )
    assert response.total_products_sold == 0


@pytest.mark.asyncio
async def test_user_metrics_response():
    response = UserMetricsResponse(
        total_users=100,
        new_users_today=5,
        new_users_week=20,
        new_users_month=50,
        active_users=30
    )
    assert response.total_users == 100
    assert response.new_users_today == 5
