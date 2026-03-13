from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order_model import Order
from app.models.order_item_model import OrderItem


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order: Order, items: List[OrderItem]) -> Order:
        self.db.add(order)
        await self.db.flush()

        for item in items:
            item.order_id = order.id
            self.db.add(item)

        await self.db.commit()
        
        # Refresh with eager loading to avoid lazy loading issues
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one()

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_user_order_by_id(self, user_id: int, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id, Order.id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_user_orders(self, user_id: int, page: int, limit: int) -> Tuple[List[Order], int]:
        offset = (page - 1) * limit

        count_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def update_order(self, order: Order) -> Order:
        await self.db.commit()
        
        # Refresh with eager loading
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one()
