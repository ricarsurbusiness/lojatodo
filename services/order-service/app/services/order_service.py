from decimal import Decimal
from typing import List, Dict, Any, Optional
import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_item_model import OrderItem
from app.models.order_model import Order, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.schemas.order_schema import OrderCreateRequest
from app.services.inventory_client import InventoryClient
from app.services.payment_client import PaymentClient


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrderRepository(db)
        self.inventory_client = InventoryClient()
        self.payment_client = PaymentClient()

    async def create_order(self, user_id: int, payload: OrderCreateRequest, user_email: str = "", token: Optional[str] = None) -> Order:
        total_amount = sum((item.quantity * item.unit_price for item in payload.items), Decimal("0"))

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            shipping_street=payload.shipping_address.street,
            shipping_city=payload.shipping_address.city,
            shipping_state=payload.shipping_address.state,
            shipping_zip_code=payload.shipping_address.zip_code,
            shipping_country=payload.shipping_address.country,
        )

        order_items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in payload.items
        ]

        order = await self.repo.create_order(order, order_items)

        reservations: List[int] = []
        try:
            for item in payload.items:
                reserve_result = await self.inventory_client.reserve(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    order_id=order.id,
                    token=token,
                )
                reservations.append(reserve_result["reservation_id"])

            order.status = OrderStatus.PROCESSING
            await self.repo.update_order(order)

            payment = await self.payment_client.charge(
                order_id=order.id,
                amount=order.total_amount,
                provider=payload.payment_provider,
                token=token,
            )

            for reservation_id in reservations:
                await self.inventory_client.confirm(reservation_id, token=token)

            order.payment_id = payment["id"]
            order.status = OrderStatus.CONFIRMED
            order = await self.repo.update_order(order)

            try:
                from app.services.event_publisher import publish_order_created
                publish_order_created(
                    order_id=order.id,
                    user_id=user_id,
                    total_amount=float(order.total_amount),
                    user_email=user_email,
                )
            except Exception:
                pass

            return order
        except httpx.HTTPStatusError:
            for reservation_id in reservations:
                try:
                    await self.inventory_client.release(reservation_id, token=token)
                except httpx.HTTPError:
                    pass
            order.status = OrderStatus.FAILED
            await self.repo.update_order(order)
            raise

    async def list_orders(self, user_id: int, page: int, limit: int):
        return await self.repo.list_user_orders(user_id=user_id, page=page, limit=limit)

    async def get_order(self, user_id: int, order_id: int) -> Optional[Order]:
        return await self.repo.get_user_order_by_id(user_id=user_id, order_id=order_id)

    async def cancel_order(self, user_id: int, order_id: int) -> Optional[Order]:
        order = await self.repo.get_user_order_by_id(user_id=user_id, order_id=order_id)
        if not order:
            return None

        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Order is already cancelled")

        if order.status not in {OrderStatus.PENDING, OrderStatus.PROCESSING}:
            raise RuntimeError("Cancellation not allowed for current status")

        order.status = OrderStatus.CANCELLED
        return await self.repo.update_order(order)

    async def ship_order(self, order_id: int, tracking_number: str, carrier: str, estimated_delivery: str) -> Optional[Order]:
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            return None

        if order.status != OrderStatus.CONFIRMED:
            raise ValueError("Only confirmed orders can be shipped")

        order.status = OrderStatus.SHIPPED
        order.tracking_number = tracking_number
        order.carrier = carrier
        order = await self.repo.update_order(order)

        try:
            from app.services.event_publisher import publish_order_shipped
            publish_order_shipped(
                order_id=order.id,
                tracking_number=tracking_number,
                carrier=carrier,
                estimated_delivery=estimated_delivery,
            )
        except Exception:
            pass

        return order
