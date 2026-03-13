from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any


class PaymentProviderBase(ABC):
    @abstractmethod
    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_method: Dict[str, Any],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        raise NotImplementedError
