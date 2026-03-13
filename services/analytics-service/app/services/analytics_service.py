from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import json
import redis.asyncio as redis

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import analytics_settings
from app.models.analytics_models import DailySalesMetric, OrderStatusMetric, ProductMetric, UserMetric
from app.schemas.analytics_schema import (
    SalesMetricsResponse, DailySales,
    OrderMetricsResponse, PeriodTrend,
    ProductMetricsResponse, ProductPerformance,
    UserMetricsResponse
)


class AnalyticsService:
    def __init__(self, db: AsyncSession, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
    
    async def get_sales_metrics(self, force_refresh: bool = False) -> SalesMetricsResponse:
        cache_key = "analytics:sales"
        
        if not force_refresh:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return SalesMetricsResponse(
                    total_revenue=Decimal(str(data["total_revenue"])),
                    today_revenue=Decimal(str(data["today_revenue"])),
                    week_revenue=Decimal(str(data["week_revenue"])),
                    month_revenue=Decimal(str(data["month_revenue"])),
                    total_orders=data["total_orders"],
                    period_details=[DailySales(**d) for d in data["period_details"]]
                )
        
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        total_result = await self.db.execute(
            select(func.sum(DailySalesMetric.revenue), func.sum(DailySalesMetric.orders_count))
            .where(DailySalesMetric.date >= month_ago)
        )
        total_row = total_result.one()
        total_revenue = total_row[0] or Decimal("0")
        total_orders = total_row[1] or 0
        
        today_result = await self.db.execute(
            select(func.sum(DailySalesMetric.revenue))
            .where(DailySalesMetric.date == today)
        )
        today_revenue = today_result.scalar() or Decimal("0")
        
        week_result = await self.db.execute(
            select(func.sum(DailySalesMetric.revenue))
            .where(DailySalesMetric.date >= week_ago)
        )
        week_revenue = week_result.scalar() or Decimal("0")
        
        month_result = await self.db.execute(
            select(func.sum(DailySalesMetric.revenue))
            .where(DailySalesMetric.date >= month_ago)
        )
        month_revenue = month_result.scalar() or Decimal("0")
        
        period_result = await self.db.execute(
            select(DailySalesMetric)
            .where(DailySalesMetric.date >= month_ago)
            .order_by(DailySalesMetric.date)
        )
        period_details = []
        for row in period_result.scalars():
            period_details.append(DailySales(
                date=row.date.isoformat(),
                revenue=row.revenue,
                orders_count=row.orders_count
            ))
        
        response = SalesMetricsResponse(
            total_revenue=total_revenue,
            today_revenue=today_revenue,
            week_revenue=week_revenue,
            month_revenue=month_revenue,
            total_orders=total_orders,
            period_details=period_details
        )
        
        cache_data = {
            "total_revenue": str(response.total_revenue),
            "today_revenue": str(response.today_revenue),
            "week_revenue": str(response.week_revenue),
            "month_revenue": str(response.month_revenue),
            "total_orders": response.total_orders,
            "period_details": [{"date": d.date, "revenue": str(d.revenue), "orders_count": d.orders_count} for d in response.period_details]
        }
        await self.redis.setex(cache_key, analytics_settings.CACHE_TTL, json.dumps(cache_data))
        
        return response
    
    async def get_order_metrics(self, force_refresh: bool = False) -> OrderMetricsResponse:
        cache_key = "analytics:orders"
        
        if not force_refresh:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return OrderMetricsResponse(
                    total_orders=data["total_orders"],
                    by_status=data["by_status"],
                    by_status_percent=data["by_status_percent"],
                    trends=[PeriodTrend(**t) for t in data["trends"]]
                )
        
        total_result = await self.db.execute(
            select(func.sum(OrderStatusMetric.count))
        )
        total_orders = total_result.scalar() or 0
        
        status_result = await self.db.execute(select(OrderStatusMetric))
        by_status = {}
        for row in status_result.scalars():
            by_status[row.status] = row.count
        
        by_status_percent = {}
        if total_orders > 0:
            for status, count in by_status.items():
                by_status_percent[status] = round(count / total_orders * 100, 2)
        
        trends = [
            PeriodTrend(period="today", orders_count=0, revenue=Decimal("0")),
            PeriodTrend(period="week", orders_count=0, revenue=Decimal("0")),
            PeriodTrend(period="month", orders_count=0, revenue=Decimal("0"))
        ]
        
        response = OrderMetricsResponse(
            total_orders=total_orders,
            by_status=by_status,
            by_status_percent=by_status_percent,
            trends=trends
        )
        
        cache_data = {
            "total_orders": response.total_orders,
            "by_status": response.by_status,
            "by_status_percent": response.by_status_percent,
            "trends": [{"period": t.period, "orders_count": t.orders_count, "revenue": str(t.revenue)} for t in response.trends]
        }
        await self.redis.setex(cache_key, analytics_settings.CACHE_TTL, json.dumps(cache_data))
        
        return response
    
    async def get_product_metrics(self, force_refresh: bool = False) -> ProductMetricsResponse:
        cache_key = "analytics:products"
        
        if not force_refresh:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return ProductMetricsResponse(
                    top_products=[ProductPerformance(**p) for p in data["top_products"]],
                    total_products_sold=data["total_products_sold"]
                )
        
        result = await self.db.execute(
            select(ProductMetric)
            .order_by(ProductMetric.units_sold.desc())
            .limit(10)
        )
        
        top_products = []
        total_products_sold = 0
        for row in result.scalars():
            top_products.append(ProductPerformance(
                product_id=row.product_id,
                product_name=row.product_name,
                units_sold=row.units_sold,
                revenue=row.revenue
            ))
            total_products_sold += row.units_sold
        
        response = ProductMetricsResponse(
            top_products=top_products,
            total_products_sold=total_products_sold
        )
        
        cache_data = {
            "top_products": [{"product_id": p.product_id, "product_name": p.product_name, "units_sold": p.units_sold, "revenue": str(p.revenue)} for p in response.top_products],
            "total_products_sold": response.total_products_sold
        }
        await self.redis.setex(cache_key, analytics_settings.CACHE_TTL, json.dumps(cache_data))
        
        return response
    
    async def get_user_metrics(self, force_refresh: bool = False) -> UserMetricsResponse:
        cache_key = "analytics:users"
        
        if not force_refresh:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return UserMetricsResponse(**data)
        
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        total_result = await self.db.execute(select(func.count(UserMetric.id)))
        total_users = total_result.scalar() or 0
        
        today_result = await self.db.execute(
            select(func.count(UserMetric.id))
            .where(UserMetric.created_at >= datetime.combine(today, datetime.min.time()))
        )
        new_users_today = today_result.scalar() or 0
        
        week_result = await self.db.execute(
            select(func.count(UserMetric.id))
            .where(UserMetric.created_at >= datetime.combine(week_ago, datetime.min.time()))
        )
        new_users_week = week_result.scalar() or 0
        
        month_result = await self.db.execute(
            select(func.count(UserMetric.id))
            .where(UserMetric.created_at >= datetime.combine(month_ago, datetime.min.time()))
        )
        new_users_month = month_result.scalar() or 0
        
        response = UserMetricsResponse(
            total_users=total_users,
            new_users_today=new_users_today,
            new_users_week=new_users_week,
            new_users_month=new_users_month,
            active_users=0
        )
        
        cache_data = response.model_dump()
        await self.redis.setex(cache_key, analytics_settings.CACHE_TTL, json.dumps(cache_data))
        
        return response
    
    async def process_order_created(self, order_id: int, user_id: int, total_amount: Decimal, created_at: datetime):
        date = created_at.date()
        
        result = await self.db.execute(
            select(DailySalesMetric).where(DailySalesMetric.date == date)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.revenue += total_amount
            existing.orders_count += 1
        else:
            new_metric = DailySalesMetric(
                date=date,
                revenue=total_amount,
                orders_count=1
            )
            self.db.add(new_metric)
        
        await self.db.commit()
        
        await self.redis.delete("analytics:sales")
    
    async def process_payment_completed(self, order_id: int, amount: Decimal, completed_at: datetime):
        status_result = await self.db.execute(
            select(OrderStatusMetric).where(OrderStatusMetric.status == "completed")
        )
        existing = status_result.scalar_one_or_none()
        
        if existing:
            existing.count += 1
        else:
            new_status = OrderStatusMetric(
                status="completed",
                count=1
            )
            self.db.add(new_status)
        
        await self.db.commit()
        
        await self.redis.delete("analytics:orders")
