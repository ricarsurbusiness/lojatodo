from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from app.models.payment_model import PaymentStatus, PaymentProvider


class PaymentChargeRequest(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    provider: PaymentProvider
    payment_method: Dict[str, Any]
    idempotency_key: str = Field(..., min_length=8, max_length=128)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    currency: str
    provider: PaymentProvider
    status: PaymentStatus
    provider_transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime


class PaymentWebhookRequest(BaseModel):
    provider: PaymentProvider
    event_type: str
    payload: Dict[str, Any]


class PaymentWebhookResponse(BaseModel):
    received: bool
    message: str
