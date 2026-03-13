import json
import pika
from typing import Any, Dict

from app.core.config import payment_settings


class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(
            payment_settings.RABBITMQ_USER,
            payment_settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=payment_settings.RABBITMQ_HOST,
            port=payment_settings.RABBITMQ_PORT,
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


def publish_payment_completed(payment_id: int, order_id: int, amount: float, provider: str):
    message = {
        "event_type": "PAYMENT_COMPLETED",
        "payment_id": payment_id,
        "order_id": order_id,
        "amount": amount,
        "provider": provider,
    }
    event_publisher.publish("PAYMENT_COMPLETED", message)


def publish_payment_failed(payment_id: int, order_id: int, amount: float, provider: str, failure_reason: str):
    message = {
        "event_type": "PAYMENT_FAILED",
        "payment_id": payment_id,
        "order_id": order_id,
        "amount": amount,
        "provider": provider,
        "failure_reason": failure_reason,
    }
    event_publisher.publish("PAYMENT_FAILED", message)
