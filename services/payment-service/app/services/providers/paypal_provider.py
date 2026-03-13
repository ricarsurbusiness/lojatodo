from decimal import Decimal
from typing import Dict, Any
import uuid

from app.services.providers.base import PaymentProviderBase


class PaypalProvider(PaymentProviderBase):
    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_method: Dict[str, Any],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        if payment_method.get("paypal_order_id") == "fail":
            return {"success": False, "error": "PayPal payment declined"}

        return {
            "success": True,
            "provider_transaction_id": f"paypal_{uuid.uuid4().hex}",
        }
