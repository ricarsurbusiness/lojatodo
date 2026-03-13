from celery import Celery
from celery.schedules import crontab

from app.core.config import analytics_settings


celery_app = Celery(
    'analytics_tasks',
    broker=analytics_settings.RABBITMQ_URL,
    backend=analytics_settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'aggregate-sales-metrics': {
            'task': 'app.tasks.aggregation_tasks.aggregate_sales_metrics',
            'schedule': crontab(minute='*/5'),
        },
        'aggregate-order-metrics': {
            'task': 'app.tasks.aggregation_tasks.aggregate_order_metrics',
            'schedule': crontab(minute='*/5'),
        },
        'aggregate-product-metrics': {
            'task': 'app.tasks.aggregation_tasks.aggregate_product_metrics',
            'schedule': crontab(minute='*/5'),
        },
        'aggregate-user-metrics': {
            'task': 'app.tasks.aggregation_tasks.aggregate_user_metrics',
            'schedule': crontab(minute='*/5'),
        },
    }
)


@celery_app.task(name='app.tasks.aggregation_tasks.aggregate_sales_metrics')
def aggregate_sales_metrics():
    pass


@celery_app.task(name='app.tasks.aggregation_tasks.aggregate_order_metrics')
def aggregate_order_metrics():
    pass


@celery_app.task(name='app.tasks.aggregation_tasks.aggregate_product_metrics')
def aggregate_product_metrics():
    pass


@celery_app.task(name='app.tasks.aggregation_tasks.aggregate_user_metrics')
def aggregate_user_metrics():
    pass
