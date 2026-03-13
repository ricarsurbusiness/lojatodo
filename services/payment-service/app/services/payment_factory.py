from app.models.payment_model import PaymentProvider
from app.services.providers.base import PaymentProviderBase
from app.services.providers.stripe_provider import StripeProvider
from app.services.providers.paypal_provider import PaypalProvider
from app.services.providers.mercadopago_provider import MercadoPagoProvider


class PaymentProviderFactory:
    @staticmethod
    def build(provider: PaymentProvider) -> PaymentProviderBase:
        if provider == PaymentProvider.STRIPE:
            return StripeProvider()
        if provider == PaymentProvider.PAYPAL:
            return PaypalProvider()
        if provider == PaymentProvider.MERCADOPAGO:
            return MercadoPagoProvider()
        raise ValueError("Unsupported payment provider")
