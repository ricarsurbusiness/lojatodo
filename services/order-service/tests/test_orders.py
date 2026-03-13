import pytest
from decimal import Decimal
from unittest.mock import AsyncMock

from app.models.order_model import OrderStatus
from app.services.order_service import OrderService
from app.schemas.order_schema import OrderCreateRequest, OrderCreateItem, ShippingAddress


@pytest.mark.asyncio
async def test_cancel_order_allows_pending_status():
    db = AsyncMock()
    service = OrderService(db)

    order = AsyncMock()
    order.id = 1
    order.status = OrderStatus.PENDING

    service.repo.get_user_order_by_id = AsyncMock(return_value=order)
    service.repo.update_order = AsyncMock(return_value=order)

    cancelled = await service.cancel_order(user_id=1, order_id=1)

    assert cancelled is order
    assert cancelled.status == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_order_rejects_confirmed_status():
    db = AsyncMock()
    service = OrderService(db)

    order = AsyncMock()
    order.status = OrderStatus.CONFIRMED

    service.repo.get_user_order_by_id = AsyncMock(return_value=order)

    with pytest.raises(RuntimeError):
        await service.cancel_order(user_id=1, order_id=1)


@pytest.mark.asyncio
async def test_create_order_releases_inventory_on_payment_failure():
    db = AsyncMock()
    service = OrderService(db)

    request = OrderCreateRequest(
        items=[OrderCreateItem(product_id=10, quantity=1, unit_price=Decimal("10.00"))],
        shipping_address=ShippingAddress(
            street="Main 123",
            city="Quito",
            state="Pichincha",
            zip_code="170101",
            country="EC",
        ),
        payment_provider="stripe",
    )

    order = AsyncMock()
    order.id = 99
    order.status = OrderStatus.PENDING
    order.total_amount = Decimal("10.00")

    service.repo.create_order = AsyncMock(return_value=order)
    service.repo.update_order = AsyncMock(return_value=order)
    service.inventory_client.reserve = AsyncMock(return_value={"reservation_id": 123})

    import httpx
    payment_response = httpx.Response(status_code=402, request=httpx.Request("POST", "http://x"))
    service.payment_client.charge = AsyncMock(side_effect=httpx.HTTPStatusError("fail", request=payment_response.request, response=payment_response))
    service.inventory_client.release = AsyncMock(return_value={"status": "released"})

    with pytest.raises(httpx.HTTPStatusError):
        await service.create_order(user_id=1, payload=request)

    service.inventory_client.release.assert_awaited_once_with(123)
