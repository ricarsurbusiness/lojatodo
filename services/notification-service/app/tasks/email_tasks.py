from datetime import datetime
from celery import Celery

from app.core.config import notification_settings
from app.services.email_service import email_service
from app.db.session import AsyncSessionLocal
from app.models.notification_model import Notification, NotificationStatus

celery_app = Celery(
    "notification_tasks",
    broker=notification_settings.CELERY_BROKER_URL,
    backend=notification_settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, notification_id: int):
    from sqlalchemy import select

    async def _send_email():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()

            if not notification:
                return

            message_id, error = email_service.send_email(
                to_email=notification.email,
                subject=notification.subject,
                body=notification.body,
            )

            if message_id:
                notification.status = NotificationStatus.SENT
                notification.sendgrid_message_id = message_id
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
                notification.failure_reason = error
                raise self.retry(exc=Exception(error))

            await db.commit()

    import asyncio
    asyncio.run(_send_email())
