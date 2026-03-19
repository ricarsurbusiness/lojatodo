from datetime import datetime
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import notification_settings
from app.services.email_service import email_service
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

# Synchronous database connection for Celery
engine = create_engine(notification_settings.DATABASE_URL_SYNC)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, notification_id: int):
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()

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
            db.commit()
        else:
            notification.status = NotificationStatus.FAILED
            notification.failure_reason = error
            db.commit()
            # Don't retry if there's no API key
            if not notification_settings.SENDGRID_API_KEY:
                return
            raise self.retry(exc=Exception(error))
    finally:
        db.close()
