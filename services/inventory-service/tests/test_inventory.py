import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from app.models.inventory_model import Inventory, InventoryReservation, ReservationStatus
from app.services.inventory_service import InventoryService


@pytest.mark.asyncio
async def test_reserve_stock_success():
    db = AsyncMock()
    service = InventoryService(db)

    inventory = Inventory(product_id=10, quantity=20, reserved_quantity=5)
    reservation = InventoryReservation(
        reservation_id=1,
        product_id=10,
        quantity=3,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        status=ReservationStatus.PENDING,
        order_id=100,
    )

    service.inventory_repo.get_inventory_with_lock = AsyncMock(return_value=inventory)
    service.inventory_repo.create_reservation = AsyncMock(return_value=reservation)
    service.inventory_repo.update_inventory = AsyncMock(return_value=inventory)

    created_reservation, error, available = await service.reserve_stock(10, 3, 100)

    assert created_reservation is reservation
    assert error is None
    assert available is None
    assert inventory.reserved_quantity == 8


@pytest.mark.asyncio
async def test_reserve_stock_insufficient_inventory():
    db = AsyncMock()
    service = InventoryService(db)

    inventory = Inventory(product_id=10, quantity=4, reserved_quantity=3)
    service.inventory_repo.get_inventory_with_lock = AsyncMock(return_value=inventory)

    created_reservation, error, available = await service.reserve_stock(10, 2, 100)

    assert created_reservation is None
    assert error == "Insufficient stock"
    assert available == 1


@pytest.mark.asyncio
async def test_confirm_reservation_expired():
    db = AsyncMock()
    service = InventoryService(db)

    reservation = InventoryReservation(
        reservation_id=1,
        product_id=10,
        quantity=2,
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        status=ReservationStatus.PENDING,
        order_id=100,
    )
    service.inventory_repo.get_reservation_with_lock = AsyncMock(return_value=reservation)

    confirmed, message = await service.confirm_reservation(1)

    assert confirmed is None
    assert "expired" in message.lower()


@pytest.mark.asyncio
async def test_release_reservation_success():
    db = AsyncMock()
    service = InventoryService(db)

    reservation = InventoryReservation(
        reservation_id=1,
        product_id=10,
        quantity=2,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        status=ReservationStatus.PENDING,
        order_id=100,
    )
    inventory = Inventory(product_id=10, quantity=20, reserved_quantity=6)

    service.inventory_repo.get_reservation_with_lock = AsyncMock(return_value=reservation)
    service.inventory_repo.get_inventory_with_lock = AsyncMock(return_value=inventory)
    service.inventory_repo.update_inventory = AsyncMock(return_value=inventory)
    service.inventory_repo.update_reservation = AsyncMock(return_value=reservation)

    released, message = await service.release_reservation(1)

    assert released is reservation
    assert message == "Success"
    assert reservation.status == ReservationStatus.RELEASED
    assert inventory.reserved_quantity == 4
