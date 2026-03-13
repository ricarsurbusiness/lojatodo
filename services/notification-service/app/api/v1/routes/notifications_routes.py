from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_notification_db
from app.schemas.notification_schema import (
    NotificationSendRequest,
    NotificationSendResponse,
    NotificationStatusResponse,
)
from app.models.notification_model import Notification, NotificationStatus
from app.tasks.email_tasks import send_email_task

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/send", response_model=NotificationSendResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    payload: NotificationSendRequest,
    db: AsyncSession = Depends(get_notification_db),
):
    if payload.correlation_id:
        existing = await db.execute(
            select(Notification).where(
                Notification.correlation_id == payload.correlation_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Notification with this correlation_id already exists"
            )

    notification = Notification(
        email=payload.email,
        subject=payload.subject,
        body=payload.body,
        status=NotificationStatus.PENDING,
        correlation_id=payload.correlation_id,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    send_email_task.delay(notification.id)

    return NotificationSendResponse(
        notification_id=notification.id,
        status=notification.status.value,
    )


@router.get("/{notification_id}", response_model=NotificationStatusResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_notification_db),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return NotificationStatusResponse(
        id=notification.id,
        email=notification.email,
        subject=notification.subject,
        body=notification.body,
        status=notification.status.value,
        correlation_id=notification.correlation_id,
        sendgrid_message_id=notification.sendgrid_message_id,
        failure_reason=notification.failure_reason,
        created_at=notification.created_at,
        sent_at=notification.sent_at,
    )
