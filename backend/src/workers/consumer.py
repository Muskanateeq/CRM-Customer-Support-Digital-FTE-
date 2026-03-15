"""
Kafka Consumer - Event Consumption
Handles Kafka consumer lifecycle and message processing
"""

import asyncio
import json
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError, KafkaTimeoutError
from aiokafka.structs import ConsumerRecord

from src.config import settings
from src.utils.logging import get_logger, set_correlation_id

logger = get_logger(__name__)


class KafkaEventConsumer:
    """
    Kafka consumer for consuming events from topics.
    Handles connection lifecycle, message deserialization, and error handling.
    """

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        handler: Callable[[Dict[str, Any]], Any],
        enable_auto_commit: bool = False,
    ):
        """
        Initialize Kafka consumer.

        Args:
            topics: List of Kafka topics to subscribe to
            group_id: Consumer group ID
            handler: Async function to handle consumed messages
            enable_auto_commit: Whether to auto-commit offsets (default: False for manual commit)
        """
        self.topics = topics
        self.group_id = group_id
        self.handler = handler
        self.enable_auto_commit = enable_auto_commit
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._is_started = False
        self._should_stop = False

    async def start(self) -> None:
        """
        Start Kafka consumer and subscribe to topics.

        Raises:
            KafkaError: If connection fails
        """
        if self._is_started:
            logger.warning("Kafka consumer already started")
            return

        try:
            logger.info(f"Starting Kafka consumer", extra={
                "topics": self.topics,
                "group_id": self.group_id,
                "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            })

            # Create consumer
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset='earliest',  # Start from beginning if no offset
                value_deserializer=self._deserialize_event,
                max_poll_records=10,  # Process 10 messages at a time
                session_timeout_ms=30000,  # 30 seconds
                heartbeat_interval_ms=10000,  # 10 seconds
            )

            # Start consumer (connects to Kafka and joins consumer group)
            await self.consumer.start()
            self._is_started = True

            logger.info("[OK] Kafka consumer started successfully", extra={
                "topics": self.topics,
                "group_id": self.group_id,
            })

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """
        Stop Kafka consumer and leave consumer group.
        Commits offsets if auto-commit is disabled.
        """
        if not self._is_started or not self.consumer:
            return

        try:
            logger.info("Stopping Kafka consumer...")
            self._should_stop = True

            # Commit any pending offsets
            if not self.enable_auto_commit:
                await self.consumer.commit()

            # Stop consumer (leaves consumer group)
            await self.consumer.stop()
            self._is_started = False

            logger.info("[OK] Kafka consumer stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {e}", exc_info=True)

    def _deserialize_event(self, raw_value: bytes) -> Dict[str, Any]:
        """
        Deserialize event from JSON bytes.

        Args:
            raw_value: JSON bytes

        Returns:
            Event dictionary
        """
        try:
            return json.loads(raw_value.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to deserialize event: {e}")
            return {}

    async def consume(self) -> None:
        """
        Start consuming messages from subscribed topics.
        Runs indefinitely until stop() is called.
        """
        if not self._is_started or not self.consumer:
            logger.error("Consumer not started, cannot consume messages")
            return

        logger.info(f"Starting message consumption loop", extra={
            "topics": self.topics,
            "group_id": self.group_id,
        })

        try:
            # Consume messages in a loop
            async for message in self.consumer:
                if self._should_stop:
                    break

                await self._process_message(message)

        except Exception as e:
            logger.error(f"Error in consumption loop: {e}", exc_info=True)
            raise

    async def consume_batch(self, timeout_ms: int = 10000) -> None:
        """
        Consume messages in batches for better throughput.
        Processes multiple messages at once and commits offsets per partition.

        Args:
            timeout_ms: Timeout for fetching batch (default: 10 seconds)
        """
        if not self._is_started or not self.consumer:
            logger.error("Consumer not started, cannot consume messages")
            return

        logger.info(f"Starting batch consumption loop", extra={
            "topics": self.topics,
            "group_id": self.group_id,
            "timeout_ms": timeout_ms,
        })

        try:
            while not self._should_stop:
                # Fetch batch of messages (grouped by topic-partition)
                message_batch = await self.consumer.getmany(timeout_ms=timeout_ms)

                if not message_batch:
                    # No messages, continue polling
                    await asyncio.sleep(1)
                    continue

                # Process each partition's messages
                for topic_partition, messages in message_batch.items():
                    if not messages:
                        continue

                    logger.debug(f"Processing batch", extra={
                        "topic": topic_partition.topic,
                        "partition": topic_partition.partition,
                        "message_count": len(messages),
                    })

                    # Process all messages in this partition
                    for message in messages:
                        await self._process_message(message)

                    # Commit offset for this partition (last message + 1)
                    if not self.enable_auto_commit:
                        await self.consumer.commit({
                            topic_partition: messages[-1].offset + 1
                        })

                        logger.debug(f"Committed offset", extra={
                            "topic": topic_partition.topic,
                            "partition": topic_partition.partition,
                            "offset": messages[-1].offset + 1,
                        })

        except Exception as e:
            logger.error(f"Error in batch consumption loop: {e}", exc_info=True)
            raise

    async def _process_message(self, message: ConsumerRecord) -> None:
        """
        Process a single message.

        Args:
            message: Kafka message record
        """
        try:
            # Extract event data
            event = message.value

            # Set correlation ID for logging
            correlation_id = event.get('correlation_id', 'unknown')
            set_correlation_id(correlation_id)

            logger.info(f"Processing message", extra={
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "event_type": event.get('event_type', 'unknown'),
                "event_id": event.get('event_id', 'unknown'),
            })

            # Call handler function
            await self.handler(event)

            logger.info(f"Message processed successfully", extra={
                "topic": message.topic,
                "offset": message.offset,
                "event_type": event.get('event_type', 'unknown'),
            })

        except Exception as e:
            logger.error(f"Failed to process message: {e}", extra={
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "event": event if 'event' in locals() else None,
            }, exc_info=True)

            # In production, send to dead letter queue
            await self._send_to_dlq(message, str(e))

    async def _send_to_dlq(self, message: ConsumerRecord, error: str) -> None:
        """
        Send failed message to dead letter queue.

        Args:
            message: Failed message
            error: Error description
        """
        try:
            logger.warning(f"Sending message to DLQ", extra={
                "topic": message.topic,
                "offset": message.offset,
                "error": error,
            })

            # In production, publish to DLQ topic
            # For now, just log
            # TODO: Implement DLQ publishing

        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}", exc_info=True)


async def create_consumer(
    topics: List[str],
    group_id: str,
    handler: Callable[[Dict[str, Any]], Any],
    enable_auto_commit: bool = False,
) -> KafkaEventConsumer:
    """
    Create and start a Kafka consumer.

    Args:
        topics: List of topics to subscribe to
        group_id: Consumer group ID
        handler: Message handler function
        enable_auto_commit: Whether to auto-commit offsets

    Returns:
        Started KafkaEventConsumer instance
    """
    consumer = KafkaEventConsumer(
        topics=topics,
        group_id=group_id,
        handler=handler,
        enable_auto_commit=enable_auto_commit,
    )
    await consumer.start()
    return consumer
