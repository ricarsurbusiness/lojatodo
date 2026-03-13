import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal


class TestOrderFlowIntegration:
    """
    Integration tests for the order flow:
    1. Create order → 2. Reserve inventory → 3. Process payment
    """

    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock()

    @pytest.fixture
    def sample_order_request(self):
        return {
            "items": [
                {"product_id": 1, "quantity": 2, "unit_price": "25.00"}
            ],
            "shipping_address": {
                "street": "Test Street 123",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "12345",
                "country": "US"
            },
            "payment_provider": "stripe"
        }

    @pytest.mark.asyncio
    async def test_order_creation_with_inventory_reservation(self, sample_order_request):
        """
        Test that order creation calls inventory service to reserve stock.
        """
        from app.services.order_service import OrderService
        
        mock_db = AsyncMock()
        service = OrderService(mock_db)
        
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "pending"
        mock_order.total_amount = Decimal("50.00")
        mock_order.items = []
        mock_order.payment_id = None
        
        service.repo.create_order = AsyncMock(return_value=mock_order)
        service.inventory_client.reserve = AsyncMock(return_value={
            "reservation_id": 123,
            "status": "reserved"
        })
        service.payment_client.charge = AsyncMock(return_value={
            "payment_id": "pay_123",
            "status": "succeeded"
        })
        
        from app.schemas.order_schema import OrderCreateRequest, OrderCreateItem, ShippingAddress
        request = OrderCreateRequest(
            items=[OrderCreateItem(product_id=1, quantity=2, unit_price=Decimal("25.00"))],
            shipping_address=ShippingAddress(
                street="Test Street 123",
                city="Test City",
                state="Test State",
                zip_code="12345",
                country="US"
            ),
            payment_provider="stripe"
        )
        
        result = await service.create_order(user_id=1, payload=request)
        
        assert result is not None
        service.inventory_client.reserve.assert_called_once()
        service.payment_client.charge.assert_called_once()

    @pytest.mark.asyncio
    async def test_order_creation_releases_inventory_on_payment_failure(self, sample_order_request):
        """
        Test that inventory is released when payment fails during order creation.
        """
        from app.services.order_service import OrderService
        
        mock_db = AsyncMock()
        service = OrderService(mock_db)
        
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "pending"
        mock_order.total_amount = Decimal("50.00")
        mock_order.items = []
        
        service.repo.create_order = AsyncMock(return_value=mock_order)
        service.inventory_client.reserve = AsyncMock(return_value={
            "reservation_id": 123,
            "status": "reserved"
        })
        service.inventory_client.release = AsyncMock(return_value={
            "status": "released"
        })
        
        payment_error = httpx.HTTPStatusError(
            "Payment failed",
            request=httpx.Request("POST", "http://payment-service/api/v1/payments/charge"),
            response=httpx.Response(402, json={"detail": "Payment failed"})
        )
        service.payment_client.charge = AsyncMock(side_effect=payment_error)
        
        from app.schemas.order_schema import OrderCreateRequest, OrderCreateItem, ShippingAddress
        request = OrderCreateRequest(
            items=[OrderCreateItem(product_id=1, quantity=2, unit_price=Decimal("25.00"))],
            shipping_address=ShippingAddress(
                street="Test Street 123",
                city="Test City",
                state="Test State",
                zip_code="12345",
                country="US"
            ),
            payment_provider="stripe"
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await service.create_order(user_id=1, payload=request)
        
        service.inventory_client.release.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_inventory_reservation_success(self):
        """
        Test successful inventory reservation.
        """
        from app.services.inventory_service import InventoryService
        from app.models.inventory_model import ReservationStatus
        
        mock_db = AsyncMock()
        service = InventoryService(mock_db)
        
        mock_inventory = MagicMock()
        mock_inventory.product_id = 1
        mock_inventory.quantity = 100
        mock_inventory.reserved_quantity = 0
        mock_inventory.available_quantity = 100
        
        service.repo.get_inventory = AsyncMock(return_value=mock_inventory)
        service.repo.create_reservation = AsyncMock(return_value=MagicMock(
            reservation_id=1,
            product_id=1,
            quantity=2,
            status=ReservationStatus.RESERVED
        ))
        service.repo.update_inventory = AsyncMock()
        
        reservation, error, available = await service.reserve_stock(
            product_id=1,
            quantity=2,
            order_id=1
        )
        
        assert error is None
        assert reservation is not None
        assert reservation.quantity == 2

    @pytest.mark.asyncio
    async def test_inventory_reservation_insufficient_stock(self):
        """
        Test that reservation fails when there's insufficient stock.
        """
        from app.services.inventory_service import InventoryService
        
        mock_db = AsyncMock()
        service = InventoryService(mock_db)
        
        mock_inventory = MagicMock()
        mock_inventory.product_id = 1
        mock_inventory.quantity = 10
        mock_inventory.reserved_quantity = 8
        mock_inventory.available_quantity = 2
        
        service.repo.get_inventory = AsyncMock(return_value=mock_inventory)
        
        reservation, error, available = await service.reserve_stock(
            product_id=1,
            quantity=5,
            order_id=1
        )
        
        assert reservation is None
        assert "insufficient" in error.lower()
        assert available == 2

    @pytest.mark.asyncio
    async def test_payment_charge_success(self):
        """
        Test successful payment charge.
        """
        from app.services.payment_service import PaymentService
        
        mock_db = AsyncMock()
        service = PaymentService(mock_db)
        
        service.provider.charge = AsyncMock(return_value={
            "payment_id": "ch_test123",
            "status": "succeeded",
            "amount": 5000
        })
        service.repo.create_payment = AsyncMock(return_value=MagicMock(
            id=1,
            external_id="ch_test123",
            amount=5000,
            status="succeeded"
        ))
        
        result = await service.process_payment(
            user_id=1,
            amount=5000,
            currency="usd",
            provider="stripe",
            order_id=1
        )
        
        assert result["status"] == "succeeded"
        assert result["payment_id"] == "ch_test123"

    @pytest.mark.asyncio
    async def test_payment_charge_failure(self):
        """
        Test payment charge failure handling.
        """
        from app.services.payment_service import PaymentService
        from app.core.exceptions import PaymentException
        
        mock_db = AsyncMock()
        service = PaymentService(mock_db)
        
        service.provider.charge = AsyncMock(side_effect=PaymentException("Card declined"))
        
        with pytest.raises(PaymentException):
            await service.process_payment(
                user_id=1,
                amount=5000,
                currency="usd",
                provider="stripe",
                order_id=1
            )

    @pytest.mark.asyncio
    async def test_order_cancel_releases_inventory(self):
        """
        Test that canceling an order releases the reserved inventory.
        """
        from app.services.order_service import OrderService
        from app.models.order_model import OrderStatus
        
        mock_db = AsyncMock()
        service = OrderService(mock_db)
        
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.status = OrderStatus.PENDING
        mock_order.reservation_id = 123
        
        service.repo.get_user_order_by_id = AsyncMock(return_value=mock_order)
        service.repo.update_order = AsyncMock(return_value=mock_order)
        service.inventory_client.release = AsyncMock(return_value={"status": "released"})
        
        result = await service.cancel_order(user_id=1, order_id=1)
        
        assert result is not None
        assert result.status == OrderStatus.CANCELLED
        service.inventory_client.release.assert_called_once()


class TestOrderInventoryPaymentIntegration:
    """
    End-to-end integration tests for order → inventory → payment flow.
    """

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires running docker-compose stack")
    async def test_full_checkout_flow(self):
        """
        Full E2E test: Create order → Reserve inventory → Process payment
        This test requires all services to be running.
        """
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                "http://localhost:8001/api/v1/auth/login",
                json={"email": "test@example.com", "password": "testpass"}
            )
            assert auth_response.status_code == 200
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            inventory_response = await client.get(
                "http://localhost:8005/api/v1/inventory/1",
                headers=headers
            )
            assert inventory_response.status_code == 200
            initial_stock = inventory_response.json()["available_quantity"]
            
            order_response = await client.post(
                "http://localhost:8004/api/v1/orders",
                headers=headers,
                json={
                    "items": [{"product_id": 1, "quantity": 2, "unit_price": "25.00"}],
                    "shipping_address": {
                        "street": "Test",
                        "city": "Test",
                        "state": "Test",
                        "zip_code": "12345",
                        "country": "US"
                    },
                    "payment_provider": "stripe"
                }
            )
            assert order_response.status_code == 201
            
            final_inventory = await client.get(
                "http://localhost:8005/api/v1/inventory/1",
                headers=headers
            )
            assert final_inventory.json()["available_quantity"] == initial_stock - 2

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires running docker-compose stack")
    async def test_order_payment_failure_releases_inventory(self):
        """
        Test that when payment fails, inventory is released.
        """
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                "http://localhost:8001/api/v1/auth/login",
                json={"email": "test@example.com", "password": "testpass"}
            )
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            initial_inventory = await client.get(
                "http://localhost:8005/api/v1/inventory/1",
                headers=headers
            )
            initial_stock = initial_inventory.json()["available_quantity"]
            
            order_response = await client.post(
                "http://localhost:8004/api/v1/orders",
                headers=headers,
                json={
                    "items": [{"product_id": 1, "quantity": 999, "unit_price": "25.00"}],
                    "shipping_address": {
                        "street": "Test",
                        "city": "Test", 
                        "state": "Test",
                        "zip_code": "12345",
                        "country": "US"
                    },
                    "payment_provider": "stripe"
                }
            )
            assert order_response.status_code in [402, 409, 502]
            
            final_inventory = await client.get(
                "http://localhost:8005/api/v1/inventory/1",
                headers=headers
            )
            assert final_inventory.json()["available_quantity"] == initial_stock
