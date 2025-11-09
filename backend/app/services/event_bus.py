"""
Event Bus service for high-availability message processing.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict, List

import aio_pika
from aio_pika import ExchangeType
from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import Event

settings = get_settings()


class EventBus:
    """High-availability event bus using RabbitMQ and Redis."""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.redis_client = None
        self.handlers: Dict[str, List[Callable]] = {}

    async def connect(self):
        """Connect to RabbitMQ and Redis."""
        # Connect to RabbitMQ
        self.connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            heartbeat=60,
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

        # Create exchange
        self.exchange = await self.channel.declare_exchange(
            "interface_agent_events",
            ExchangeType.TOPIC,
            durable=True,
        )

        # Connect to Redis for caching and deduplication
        self.redis_client = Redis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )

    async def disconnect(self):
        """Disconnect from RabbitMQ and Redis."""
        if self.connection:
            await self.connection.close()
        if self.redis_client:
            await self.redis_client.close()

    async def publish(self, event_type: str, payload: Dict[str, Any], source: str = "system"):
        """Publish an event to the event bus."""
        # Store event in database
        async with AsyncSessionLocal() as db:
            event = Event(
                event_type=event_type,
                source=source,
                payload=payload,
                status="pending",
            )
            db.add(event)
            await db.commit()
            await db.refresh(event)
            event_id = event.id

        # Publish to RabbitMQ
        message = aio_pika.Message(
            body=json.dumps(
                {
                    "event_id": event_id,
                    "event_type": event_type,
                    "source": source,
                    "payload": payload,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.exchange.publish(
            message,
            routing_key=event_type,
        )

        return event_id

    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

        # Create queue for this event type
        queue = await self.channel.declare_queue(
            f"queue_{event_type}",
            durable=True,
        )

        await queue.bind(self.exchange, routing_key=event_type)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode())
                event_id = data.get("event_id")

                # Check deduplication in Redis
                cache_key = f"event_processed:{event_id}"
                if await self.redis_client.exists(cache_key):
                    return  # Already processed

                try:
                    # Call all handlers
                    for h in self.handlers[event_type]:
                        await h(data)

                    # Mark as processed in Redis (TTL 24 hours)
                    await self.redis_client.setex(cache_key, 86400, "1")

                    # Update event status in database
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(select(Event).where(Event.id == event_id))
                        event = result.scalar_one_or_none()
                        if event:
                            event.status = "completed"
                            event.processed_at = datetime.utcnow()
                            await db.commit()

                except Exception as e:
                    # Update event status to failed
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(select(Event).where(Event.id == event_id))
                        event = result.scalar_one_or_none()
                        if event:
                            event.status = "failed"
                            event.retry_count += 1
                            await db.commit()
                    raise

        await queue.consume(process_message)


# Global event bus instance
event_bus = EventBus()
