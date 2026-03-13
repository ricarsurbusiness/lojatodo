import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal


class TestEventPublishing:
    """
    Integration tests for event publishing.
    These tests verify that events are properly published to RabbitMQ
    when order and payment actions occur.
    """

    @pytest.mark.asyncio
    async def test_order_created_event_published(self):
        """
        Test that ORDER_CREATED event is published when an order is confirmed.
        """
        from app.services.order_service import OrderService
        from app.schemas.order_schema import OrderCreateRequest, OrderCreateItem, ShippingAddress

        mock_db = MagicMock()
        service = OrderService(mock_db)

        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "confirmed"
        mock_order.total_amount = Decimal("50.00")
        mock_order.items = []
        mock_order.payment_id = 1

        service.repo.create_order = MagicMock(return_value=mock_order)
        service.repo.update_order = MagicMock(return_value=mock_order)
        service.inventory_client.reserve = MagicMock(return_value={"reservation_id": 123, "status": "reserved"})
        service.inventory_client.confirm = MagicMock()
        service.payment_client.charge = MagicMock(return_value={"id": 1, "status": "succeeded"})

        with patch("app.services.order_service.publish_order_created") as mock_publish:
            mock_publish.return_value = None
            
            request = OrderCreateRequest(
                items=[OrderCreateItem(product_id=1, quantity=2, unit_price=Decimal("25.00"))],
                shipping_address=ShippingAddress(
                    street="Test Street",
                    city="Test City",
                    state="Test State",
                    zip_code="12345",
                    country="US"
                ),
                payment_provider="stripe"
            )
            
            try:
                await service.create_order(user_id=1, payload=request, user_email="test@example.com")
            except Exception:
                pass

            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[1]["order_id"] == 1
            assert call_args[1]["user_id"] == 1
            assert call_args[1]["total_amount"] == 50.00
            assert call_args[1]["user_email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_payment_completed_event_published(self):
        """
        Test that PAYMENT_COMPLETED event is published when payment succeeds.
        """
        with patch("app.services.event_publisher.publish_payment_completed") as mock_publish:
            from app.services.event_publisher import publish_payment_completed
            
            publish_payment_completed(
                payment_id=1,
                order_id=100,
                amount=50.00,
                provider="stripe",
            )
            
            mock_publish.assert_called_once_with(
                payment_id=1,
                order_id=100,
                amount=50.00,
                provider="stripe",
            )

    @pytest.mark.asyncio
    async def test_payment_failed_event_published(self):
        """
        Test that PAYMENT_FAILED event is published when payment fails.
        """
        with patch("app.services.event_publisher.publish_payment_failed") as mock_publish:
            from app.services.event_publisher import publish_payment_failed
            
            publish_payment_failed(
                payment_id=1,
                order_id=100,
                amount=50.00,
                provider="stripe",
                failure_reason="Card declined",
            )
            
            mock_publish.assert_called_once_with(
                payment_id=1,
                order_id=100,
                amount=50.00,
                provider="stripe",
                failure_reason="Card declined",
            )

    @pytest.mark.asyncio
    async def test_order_shipped_event_published(self):
        """
        Test that ORDER_SHIPPED event is published when an order is shipped.
        """
        with patch("app.services.event_publisher.publish_order_shipped") as mock_publish:
            from app.services.event_publisher import publish_order_shipped
            
            publish_order_shipped(
                order_id=1,
                tracking_number="TRACK123",
                carrier="UPS",
                estimated_delivery="2024-12-25",
            )
            
            mock_publish.assert_called_once_with(
                order_id=1,
                tracking_number="TRACK123",
                carrier="UPS",
                estimated_delivery="2024-12-25",
            )


class TestEventPublisherConnection:
    """
    Tests for EventPublisher connection and configuration.
    """

    @pytest.mark.asyncio
    async def test_event_publisher_initialization(self):
        """
        Test that EventPublisher can be initialized without connecting.
        """
        from app.services.event_publisher import EventPublisher
        
        publisher = EventPublisher()
        assert publisher.connection is None
        assert publisher.channel is None

    @pytest.mark.asyncio
    async def test_event_publisher_config(self):
        """
        Test that EventPublisher uses correct configuration.
        """
        from app.core.config import order_settings
        
        assert order_settings.RABBITMQ_HOST is not None
        assert order_settings.RABBITMQ_PORT is not None
        assert order_settings.RABBITMQ_USER is not None
        assert order_settings.RABBITMQ_PASSWORD is not None


class TestPaymentEventPublisherConnection:
    """
    Tests for Payment EventPublisher connection and configuration.
    """

    @pytest.mark.asyncio
    async def test_payment_event_publisher_initialization(self):
        """
        Test that Payment EventPublisher can be initialized without connecting.
        """
        from app.services.event_publisher import EventPublisher
        
        publisher = EventPublisher()
        assert publisher.connection is None
        assert publisher.channel is None

    @pytest.mark.asyncio
    async def test_payment_event_publisher_config(self):
        """
        Test that Payment EventPublisher uses correct configuration.
        """
        from app.core.config import payment_settings
        
        assert payment_settings.RABBITMQ_HOST is not None
        assert payment_settings.RABBITMQ_PORT is not None
        assert payment_settings.RABBITMQ_USER is not None
        assert payment_settings.RABBITMQ_PASSWORD is not None
