import json
import pika
import threading
from typing import Callable, Dict, Any

from app.core.config import notification_settings


class EventConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.handlers: Dict[str, Callable] = {}

    def connect(self):
        credentials = pika.PlainCredentials(
            notification_settings.RABBITMQ_USER,
            notification_settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=notification_settings.RABBITMQ_HOST,
            port=notification_settings.RABBITMQ_PORT,
            credentials=credentials,
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange="events",
            exchange_type="topic",
            durable=True,
        )

    def register_handler(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler

    def _on_message(self, channel, method, properties, body):
        try:
            message = json.loads(body)
            event_type = message.get("event_type")

            if event_type in self.handlers:
                self.handlers[event_type](message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self, queue_name: str, routing_keys: list):
        if not self.channel:
            self.connect()

        self.channel.queue_declare(queue=queue_name, durable=True)

        for routing_key in routing_keys:
            self.channel.queue_bind(
                exchange="events",
                queue=queue_name,
                routing_key=routing_key,
            )

        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._on_message,
        )

        print(f"Starting consumer for queue: {queue_name}")
        self.channel.start_consuming()

    def start_in_background(self, queue_name: str, routing_keys: list):
        thread = threading.Thread(
            target=self.start_consuming,
            args=(queue_name, routing_keys),
            daemon=True,
        )
        thread.start()
        return thread

    def close(self):
        if self.connection:
            self.connection.close()


def handle_order_created(message: Dict[str, Any]):
    from app.tasks.email_tasks import send_email_task
    from app.db.session import AsyncSessionLocal
    from app.models.notification_model import Notification, NotificationStatus
    import asyncio

    user_email = message.get("user_email")
    order_id = message.get("order_id")
    total_amount = message.get("total_amount")

    subject = f"Order Confirmation - Order #{order_id}"
    body = f"""
    <html>
    <body>
        <h2>Thank you for your order!</h2>
        <p>Your order #{order_id} has been confirmed.</p>
        <p>Total amount: ${total_amount}</p>
        <p>We will notify you when your order ships.</p>
    </body>
    </html>
    """

    async def _create_notification():
        async with AsyncSessionLocal() as db:
            notification = Notification(
                email=user_email,
                subject=subject,
                body=body,
                status=NotificationStatus.PENDING,
                correlation_id=f"order_{order_id}",
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            send_email_task.delay(notification.id)

    asyncio.run(_create_notification())


def handle_payment_completed(message: Dict[str, Any]):
    from app.tasks.email_tasks import send_email_task
    from app.db.session import AsyncSessionLocal
    from app.models.notification_model import Notification, NotificationStatus
    import asyncio

    order_id = message.get("order_id")
    amount = message.get("amount")

    subject = f"Payment Confirmed - Order #{order_id}"
    body = f"""
    <html>
    <body>
        <h2>Payment Confirmed!</h2>
        <p>Your payment of ${amount} for order #{order_id} has been processed successfully.</p>
        <p>Thank you for shopping with us!</p>
    </body>
    </html>
    """

    async def _create_notification():
        async with AsyncSessionLocal() as db:
            notification = Notification(
                email="customer@example.com",
                subject=subject,
                body=body,
                status=NotificationStatus.PENDING,
                correlation_id=f"payment_{message.get('payment_id')}",
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            send_email_task.delay(notification.id)

    asyncio.run(_create_notification())


def handle_payment_failed(message: Dict[str, Any]):
    from app.tasks.email_tasks import send_email_task
    from app.db.session import AsyncSessionLocal
    from app.models.notification_model import Notification, NotificationStatus
    import asyncio

    order_id = message.get("order_id")

    subject = f"Payment Failed - Order #{order_id}"
    body = f"""
    <html>
    <body>
        <h2>Payment Failed</h2>
        <p>Unfortunately, the payment for your order #{order_id} could not be processed.</p>
        <p>Please update your payment method and try again.</p>
    </body>
    </html>
    """

    async def _create_notification():
        async with AsyncSessionLocal() as db:
            notification = Notification(
                email="customer@example.com",
                subject=subject,
                body=body,
                status=NotificationStatus.PENDING,
                correlation_id=f"payment_failed_{message.get('payment_id')}",
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            send_email_task.delay(notification.id)

    asyncio.run(_create_notification())


def handle_order_shipped(message: Dict[str, Any]):
    from app.tasks.email_tasks import send_email_task
    from app.db.session import AsyncSessionLocal
    from app.models.notification_model import Notification, NotificationStatus
    import asyncio

    order_id = message.get("order_id")
    tracking_number = message.get("tracking_number")
    carrier = message.get("carrier")
    estimated_delivery = message.get("estimated_delivery")

    subject = f"Order Shipped - Order #{order_id}"
    body = f"""
    <html>
    <body>
        <h2>Your order has shipped!</h2>
        <p>Order #{order_id} is on its way.</p>
        <p>Carrier: {carrier}</p>
        <p>Tracking Number: {tracking_number}</p>
        <p>Estimated Delivery: {estimated_delivery}</p>
    </body>
    </html>
    """

    async def _create_notification():
        async with AsyncSessionLocal() as db:
            notification = Notification(
                email="customer@example.com",
                subject=subject,
                body=body,
                status=NotificationStatus.PENDING,
                correlation_id=f"shipped_{order_id}",
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            send_email_task.delay(notification.id)

    asyncio.run(_create_notification())


event_consumer = EventConsumer()

event_consumer.register_handler("ORDER_CREATED", handle_order_created)
event_consumer.register_handler("PAYMENT_COMPLETED", handle_payment_completed)
event_consumer.register_handler("PAYMENT_FAILED", handle_payment_failed)
event_consumer.register_handler("ORDER_SHIPPED", handle_order_shipped)
