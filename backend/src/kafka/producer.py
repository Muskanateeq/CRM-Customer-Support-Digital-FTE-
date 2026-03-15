"""
Kafka Producer - Event Publishing
Handles Kafka producer lifecycle and event publishing
"""

import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError

from src.config import settings
from src.utils.logging import get_logger, get_correlation_id
from src.kafka.events import BaseEvent

logger = get_logger(__name__)


class KafkaEventProducer:
    """
    Kafka producer for publishing events.
    Handles connection lifecycle and message serialization.
    """

    def __init__(self):
        """Initialize Kafka producer."""
        self.producer: Optional[AIOKafkaProducer] = None
        self._is_started = False

    async def start(self) -> None:
        """
        Start Kafka producer and establish connection.

        Raises:
            KafkaError: If connection fails
        """
        if self._is_started:
            logger.warning("Kafka producer already started")
            return

        try:
            logger.info(f"Starting Kafka producer", extra={
                "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS
            })

            # Create producer with JSON serialization
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=self._serialize_event,
                compression_type="gzip",  # Compress messages
                enable_idempotence=True,  # Prevent duplicates on retry
                acks='all',  # Wait for all replicas
                request_timeout_ms=30000,  # 30 second timeout
                retry_backoff_ms=100,
            )

            # Start producer (connects to Kafka)
            await self.producer.start()
            self._is_started = True

            logger.info("[OK] Kafka producer started successfully")

        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """
        Stop Kafka producer and close connections.
        Waits for pending messages to be delivered.
        """
        if not self._is_started or not self.producer:
            return

        try:
            logger.info("Stopping Kafka producer...")

            # Wait for all pending messages to be delivered
            await self.producer.stop()
            self._is_started = False

            logger.info("[OK] Kafka producer stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}", exc_info=True)

    def _serialize_event(self, event: Dict[str, Any]) -> bytes:
        """
        Serialize event to JSON bytes.

        Args:
            event: Event dictionary

        Returns:
            JSON bytes
        """
        # Convert datetime objects to ISO format
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat() + 'Z'
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(event, default=json_serializer).encode('utf-8')

    async def publish_event(
        self,
        topic: str,
        event: BaseEvent,
        key: Optional[str] = None
    ) -> bool:
        """
        Publish event to Kafka topic.

        Args:
            topic: Kafka topic name
            event: Event object (Pydantic model)
            key: Optional message key for partitioning

        Returns:
            True if published successfully, False otherwise
        """
        if not self._is_started or not self.producer:
            logger.error("Kafka producer not started, cannot publish event")
            return False

        try:
            # Add correlation ID if not present
            if not event.correlation_id:
                event.correlation_id = get_correlation_id()

            # Add event ID if not present
            if not event.event_id:
                event.event_id = str(uuid.uuid4())

            # Convert Pydantic model to dict
            event_dict = event.model_dump(mode='json')

            # Encode key if provided
            key_bytes = key.encode('utf-8') if key else None

            logger.debug(f"Publishing event to Kafka", extra={
                "topic": topic,
                "event_type": event.event_type,
                "event_id": event.event_id,
            })

            # Send message and wait for acknowledgment
            await self.producer.send_and_wait(
                topic,
                value=event_dict,
                key=key_bytes
            )

            logger.info(f"Event published successfully", extra={
                "topic": topic,
                "event_type": event.event_type,
                "event_id": event.event_id,
            })

            return True

        except KafkaTimeoutError as e:
            logger.error(f"Kafka timeout while publishing event: {e}", extra={
                "topic": topic,
                "event_type": event.event_type,
            })
            return False

        except KafkaError as e:
            logger.error(f"Kafka error while publishing event: {e}", extra={
                "topic": topic,
                "event_type": event.event_type,
            }, exc_info=True)
            return False

        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}", extra={
                "topic": topic,
                "event_type": event.event_type if hasattr(event, 'event_type') else 'unknown',
            }, exc_info=True)
            return False

    async def publish_event_fire_and_forget(
        self,
        topic: str,
        event: BaseEvent,
        key: Optional[str] = None
    ) -> None:
        """
        Publish event without waiting for acknowledgment (fire and forget).
        Faster but less reliable.

        Args:
            topic: Kafka topic name
            event: Event object
            key: Optional message key
        """
        if not self._is_started or not self.producer:
            logger.error("Kafka producer not started, cannot publish event")
            return

        try:
            # Add correlation ID and event ID
            if not event.correlation_id:
                event.correlation_id = get_correlation_id()
            if not event.event_id:
                event.event_id = str(uuid.uuid4())

            # Convert to dict
            event_dict = event.model_dump(mode='json')

            # Encode key
            key_bytes = key.encode('utf-8') if key else None

            # Send without waiting (fire and forget)
            await self.producer.send(
                topic,
                value=event_dict,
                key=key_bytes
            )

            logger.debug(f"Event sent (fire and forget)", extra={
                "topic": topic,
                "event_type": event.event_type,
            })

        except Exception as e:
            logger.error(f"Error sending event (fire and forget): {e}", extra={
                "topic": topic,
                "event_type": event.event_type if hasattr(event, 'event_type') else 'unknown',
            })


# Global producer instance
_producer_instance: Optional[KafkaEventProducer] = None


async def get_kafka_producer() -> KafkaEventProducer:
    """
    Get or create global Kafka producer instance.

    Returns:
        KafkaEventProducer instance
    """
    global _producer_instance

    if _producer_instance is None:
        _producer_instance = KafkaEventProducer()
        await _producer_instance.start()

    return _producer_instance


async def publish_event(topic: str, event: BaseEvent, key: Optional[str] = None) -> bool:
    """
    Convenience function to publish event using global producer.

    Args:
        topic: Kafka topic name
        event: Event object
        key: Optional message key

    Returns:
        True if published successfully
    """
    producer = await get_kafka_producer()
    return await producer.publish_event(topic, event, key)
