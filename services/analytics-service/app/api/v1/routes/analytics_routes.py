from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.dependencies import get_current_user, CurrentUser, get_redis
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schema import (
    SalesMetricsResponse,
    OrderMetricsResponse,
    ProductMetricsResponse,
    UserMetricsResponse
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sales", response_model=SalesMetricsResponse)
async def get_sales_analytics(
    refresh: bool = Query(False, description="Force refresh cache"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    analytics_service = AnalyticsService(db, redis_client)
    return await analytics_service.get_sales_metrics(force_refresh=refresh)


@router.get("/orders", response_model=OrderMetricsResponse)
async def get_order_analytics(
    refresh: bool = Query(False, description="Force refresh cache"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    analytics_service = AnalyticsService(db, redis_client)
    return await analytics_service.get_order_metrics(force_refresh=refresh)


@router.get("/products", response_model=ProductMetricsResponse)
async def get_product_analytics(
    refresh: bool = Query(False, description="Force refresh cache"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    analytics_service = AnalyticsService(db, redis_client)
    return await analytics_service.get_product_metrics(force_refresh=refresh)


@router.get("/users", response_model=UserMetricsResponse)
async def get_user_analytics(
    refresh: bool = Query(False, description="Force refresh cache"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    analytics_service = AnalyticsService(db, redis_client)
    return await analytics_service.get_user_metrics(force_refresh=refresh)
