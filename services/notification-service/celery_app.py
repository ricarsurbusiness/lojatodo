from celery import Celery

from app.core.config import notification_settings

celery_app = Celery(
    "notification_service",
    broker=notification_settings.CELERY_BROKER_URL,
    backend=notification_settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

if __name__ == "__main__":
    celery_app.start()
