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
        
        # First, reserve inventory for all items BEFORE creating the order
        reservations: List[int] = []
        try:
            for item in payload.items:
                reserve_result = await self.inventory_client.reserve(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    order_id=0,  # Temporary ID, will be updated after order creation
                    token=token,
                )
                reservations.append(reserve_result["reservation_id"])
        except httpx.HTTPStatusError as e:
            # If any inventory reservation fails, raise immediately without creating order
            raise

        # Now create the order since inventory is reserved
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
        
        # Store reservation_ids in order metadata for later use
        # For now, we'll keep the order in PENDING status
        # User must call /confirm endpoint to process payment
        
        return order

    async def delete_order(self, order_id: int) -> bool:
        """Delete an order by ID"""
        return await self.repo.delete_order(order_id)

    async def list_orders(self, user_id: int, page: int, limit: int):
        return await self.repo.list_user_orders(user_id=user_id, page=page, limit=limit)

    async def get_order(self, user_id: int, order_id: int) -> Optional[Order]:
        return await self.repo.get_user_order_by_id(user_id=user_id, order_id=order_id)

    async def cancel_order(self, user_id: int, order_id: int, token: Optional[str] = None) -> Optional[Order]:
        order = await self.repo.get_user_order_by_id(user_id=user_id, order_id=order_id)
        if not order:
            return None

        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Order is already cancelled")

        # Can only cancel PENDING, CONFIRMED, or FAILED orders
        if order.status not in {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.FAILED}:
            raise RuntimeError("Cancellation not allowed for current status")

        # Release inventory if order was confirmed (inventory was committed)
        if order.status == OrderStatus.CONFIRMED:
            # Get reservations from inventory and release them
            # Note: We need to track reservation_ids - for now we'll skip this
            # In a real scenario, you'd store reservation_ids in the order
            pass

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

    async def list_all_orders(self, page: int, limit: int):
        return await self.repo.list_all_orders(page=page, limit=limit)

    async def count_all_orders(self) -> int:
        return await self.repo.count_all_orders()

    async def deliver_order(self, order_id: int) -> Optional[Order]:
        """Mark an order as delivered"""
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            return None

        if order.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be delivered")

        order.status = OrderStatus.DELIVERED
        return await self.repo.update_order(order)

    async def confirm_order(self, order_id: int, user_email: str = "", token: Optional[str] = None) -> Optional[Order]:
        """Confirm a pending order (process payment)"""
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            return None

        if order.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")

        try:
            payment = await self.payment_client.charge(
                order_id=order.id,
                amount=order.total_amount,
                provider="stripe",  # Default provider
                token=token,
            )

            order.payment_id = payment["id"]
            order.status = OrderStatus.CONFIRMED
            order = await self.repo.update_order(order)

            try:
                from app.services.event_publisher import publish_order_created
                publish_order_created(
                    order_id=order.id,
                    user_id=order.user_id,
                    total_amount=float(order.total_amount),
                    user_email=user_email,
                )
            except Exception:
                pass

            return order
        except httpx.HTTPStatusError:
            order.status = OrderStatus.FAILED
            await self.repo.update_order(order)
            raise
