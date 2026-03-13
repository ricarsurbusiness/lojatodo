from decimal import Decimal
from typing import Dict, Any, Optional
import uuid
import httpx

from app.core.config import order_settings


class PaymentClient:
    async def charge(
        self,
        order_id: int,
        amount: Decimal,
        provider: str,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{order_settings.PAYMENT_SERVICE_URL}/api/v1/payments/charge",
                json={
                    "order_id": order_id,
                    "amount": str(amount),
                    "currency": "USD",
                    "provider": provider,
                    "payment_method": {"source": "order-service"},
                    "idempotency_key": f"ord_{order_id}_{uuid.uuid4().hex[:16]}",
                },
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
