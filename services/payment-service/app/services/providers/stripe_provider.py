from decimal import Decimal
from typing import Dict, Any
import uuid

from app.services.providers.base import PaymentProviderBase


class StripeProvider(PaymentProviderBase):
    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_method: Dict[str, Any],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        if payment_method.get("card_token") == "fail":
            return {"success": False, "error": "Stripe payment declined"}

        return {
            "success": True,
            "provider_transaction_id": f"stripe_{uuid.uuid4().hex}",
        }
