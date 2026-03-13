import json
import asyncio
import pika
from typing import Callable, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.core.config import analytics_settings


class EventConsumer:
    def __init__(self, message_handler: Callable[[Dict[str, Any]], None]):
        self.message_handler = message_handler
        self.connection = None
        self.channel = None
    
    def connect(self):
        parameters = pika.ConnectionParameters(
            host=analytics_settings.RABBITMQ_HOST,
            port=analytics_settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                analytics_settings.RABBITMQ_USER,
                analytics_settings.RABBITMQ_PASSWORD
            )
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(
            exchange='events',
            exchange_type='topic',
            durable=True
        )
    
    def start_consuming(self):
        if not self.channel:
            self.connect()
        
        result = self.channel.queue_declare(queue='analytics', durable=True)
        queue_name = result.method.queue
        
        self.channel.queue_bind(
            exchange='events',
            queue=queue_name,
            routing_key='order.*'
        )
        
        self.channel.queue_bind(
            exchange='events',
            queue=queue_name,
            routing_key='payment.*'
        )
        
        self.channel.basic_qos(prefetch_count=10)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._on_message
        )
        
        print('Analytics service started consuming events...')
        self.channel.start_consuming()
    
    def _on_message(self, channel, method, properties, body):
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            
            print(f'Received event: {event_type}')
            
            self.message_handler(message)
            
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f'Error processing message: {e}')
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def close(self):
        if self.connection:
            self.connection.close()


async def process_event(message: Dict[str, Any]):
    from app.db.session import AsyncSessionLocal
    from app.services.analytics_service import AnalyticsService
    from app.core.dependencies import get_redis
    
    async with AsyncSessionLocal() as db:
        redis_client = await get_redis()
        analytics_service = AnalyticsService(db, redis_client)
        
        event_type = message.get('event_type')
        
        if event_type == 'ORDER_CREATED':
            await analytics_service.process_order_created(
                order_id=message['order_id'],
                user_id=message['user_id'],
                total_amount=Decimal(str(message['total_amount'])),
                created_at=datetime.fromisoformat(message['created_at'])
            )
        
        elif event_type == 'PAYMENT_COMPLETED':
            await analytics_service.process_payment_completed(
                order_id=message['order_id'],
                amount=Decimal(str(message['amount'])),
                completed_at=datetime.fromisoformat(message['completed_at'])
            )


def start_consumer():
    consumer = EventConsumer(process_event)
    consumer.start_consuming()
