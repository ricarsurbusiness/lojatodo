import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.models.payment_model import PaymentProvider, PaymentStatus
from app.services.payment_factory import PaymentProviderFactory
from app.services.providers.stripe_provider import StripeProvider
from app.services.providers.paypal_provider import PaypalProvider
from app.services.providers.mercadopago_provider import MercadoPagoProvider


def test_payment_factory_returns_stripe_provider():
    provider = PaymentProviderFactory.build(PaymentProvider.STRIPE)
    assert isinstance(provider, StripeProvider)


def test_payment_factory_returns_paypal_provider():
    provider = PaymentProviderFactory.build(PaymentProvider.PAYPAL)
    assert isinstance(provider, PaypalProvider)


def test_payment_factory_returns_mercadopago_provider():
    provider = PaymentProviderFactory.build(PaymentProvider.MERCADOPAGO)
    assert isinstance(provider, MercadoPagoProvider)


@pytest.mark.asyncio
async def test_stripe_provider_success():
    provider = StripeProvider()
    result = await provider.charge(
        amount=Decimal("10.00"),
        currency="USD",
        payment_method={"card_token": "tok_test"},
        idempotency_key="idem_12345678",
    )
    assert result["success"] is True
    assert "provider_transaction_id" in result


@pytest.mark.asyncio
async def test_stripe_provider_failure():
    provider = StripeProvider()
    result = await provider.charge(
        amount=Decimal("10.00"),
        currency="USD",
        payment_method={"card_token": "fail"},
        idempotency_key="idem_12345678",
    )
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_payment_completed_event_published():
    """Test that PAYMENT_COMPLETED event is published on successful payment."""
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
async def test_payment_failed_event_published():
    """Test that PAYMENT_FAILED event is published on failed payment."""
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


def test_payment_event_publisher_config():
    """Test that payment event publisher has correct configuration."""
    from app.core.config import payment_settings
    
    assert payment_settings.RABBITMQ_HOST is not None
    assert payment_settings.RABBITMQ_PORT == 5672
    assert payment_settings.RABBITMQ_USER == "guest"
    assert payment_settings.RABBITMQ_PASSWORD == "guest"
