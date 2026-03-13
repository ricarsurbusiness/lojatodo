import json
import pika
from typing import Any, Dict

from app.core.config import order_settings


class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(
            order_settings.RABBITMQ_USER,
            order_settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=order_settings.RABBITMQ_HOST,
            port=order_settings.RABBITMQ_PORT,
            credentials=credentials,
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange="events",
            exchange_type="topic",
            durable=True,
        )

    def publish(self, event_type: str, message: Dict[str, Any]):
        if not self.channel:
            self.connect()

        self.channel.basic_publish(
            exchange="events",
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

    def close(self):
        if self.connection:
            self.connection.close()


event_publisher = EventPublisher()


def publish_order_created(order_id: int, user_id: int, total_amount: float, user_email: str):
    message = {
        "event_type": "ORDER_CREATED",
        "order_id": order_id,
        "user_id": user_id,
        "total_amount": total_amount,
        "user_email": user_email,
    }
    event_publisher.publish("ORDER_CREATED", message)


def publish_order_shipped(order_id: int, tracking_number: str, carrier: str, estimated_delivery: str):
    message = {
        "event_type": "ORDER_SHIPPED",
        "order_id": order_id,
        "tracking_number": tracking_number,
        "carrier": carrier,
        "estimated_delivery": estimated_delivery,
    }
    event_publisher.publish("ORDER_SHIPPED", message)
