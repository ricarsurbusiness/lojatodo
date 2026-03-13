from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, CurrentUser
from app.db.session import get_db
from app.models.payment_model import Payment, PaymentStatus
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment_schema import (
    PaymentChargeRequest,
    PaymentResponse,
    PaymentWebhookRequest,
    PaymentWebhookResponse,
)
from app.services.payment_factory import PaymentProviderFactory

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/charge", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def charge_payment(
    request: PaymentChargeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PaymentRepository(db)

    existing = await repo.get_by_idempotency_key(request.idempotency_key)
    if existing:
        return PaymentResponse.model_validate(existing)

    provider = PaymentProviderFactory.build(request.provider)
    result = await provider.charge(
        amount=request.amount,
        currency=request.currency,
        payment_method=request.payment_method,
        idempotency_key=request.idempotency_key,
    )

    payment = Payment(
        order_id=request.order_id,
        amount=request.amount,
        currency=request.currency,
        provider=request.provider,
        status=PaymentStatus.SUCCEEDED if result.get("success") else PaymentStatus.FAILED,
        provider_transaction_id=result.get("provider_transaction_id"),
        idempotency_key=request.idempotency_key,
        failure_reason=result.get("error"),
    )
    payment = await repo.create(payment)

    if payment.status == PaymentStatus.FAILED:
        try:
            from app.services.event_publisher import publish_payment_failed
            publish_payment_failed(
                payment_id=payment.id,
                order_id=payment.order_id,
                amount=float(payment.amount),
                provider=payment.provider,
                failure_reason=payment.failure_reason or "Payment failed",
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=payment.failure_reason or "Payment failed",
        )

    try:
        from app.services.event_publisher import publish_payment_completed
        publish_payment_completed(
            payment_id=payment.id,
            order_id=payment.order_id,
            amount=float(payment.amount),
            provider=payment.provider,
        )
    except Exception:
        pass

    return PaymentResponse.model_validate(payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PaymentRepository(db)
    payment = await repo.get_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentResponse.model_validate(payment)


@router.post("/webhook", response_model=PaymentWebhookResponse)
async def payment_webhook(
    request: PaymentWebhookRequest,
    db: AsyncSession = Depends(get_db),
):
    return PaymentWebhookResponse(
        received=True,
        message=f"Webhook received for provider={request.provider} event={request.event_type}",
    )
