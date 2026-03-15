"""
Worker Service - Manages Kafka Consumers
Runs multiple consumers in parallel for different topics
"""

import asyncio
import signal
from typing import List, Optional
from datetime import datetime

from src.config import settings
from src.utils.logging import setup_logging, get_logger
from src.database.client import init_db_pool, close_db_pool
from src.workers.consumer import create_consumer
from src.workers.handlers import route_event
from src.kafka.topics import KafkaTopics

logger = get_logger(__name__)


class WorkerService:
    """
    Worker service that manages multiple Kafka consumers.
    Each consumer runs in a separate task for parallel processing.
    """

    def __init__(self):
        """Initialize worker service."""
        self.consumers: List = []
        self.tasks: List[asyncio.Task] = []
        self._should_stop = False

    async def start(self) -> None:
        """
        Start worker service.
        Initializes database and creates consumers for all topics.
        """
        try:
            logger.info("=" * 70)
            logger.info("Custora Worker Service - Starting Up")
            logger.info("=" * 70)
            logger.info(f"Environment: {settings.ENVIRONMENT}")
            logger.info(f"Kafka Bootstrap: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            logger.info("=" * 70)

            # Initialize database
            await init_db_pool()
            logger.info("[OK] Database pool initialized")

            # Create consumers for each topic
            await self._create_consumers()

            # Start consumption tasks
            await self._start_consumption()

            logger.info("=" * 70)
            logger.info("[OK] Worker Service Started - Ready to Process Events")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Failed to start worker service: {e}", exc_info=True)
            raise

    async def _create_consumers(self) -> None:
        """Create Kafka consumers for all topics."""

        # Consumer configuration
        consumer_configs = [
            {
                'topics': [KafkaTopics.MESSAGE_RECEIVED],
                'group_id': 'custora-message-received-workers',
                'handler': route_event,
            },
            {
                'topics': [KafkaTopics.MESSAGE_SENT],
                'group_id': 'custora-message-sent-workers',
                'handler': route_event,
            },
            {
                'topics': [KafkaTopics.ESCALATION_CREATED],
                'group_id': 'custora-escalation-workers',
                'handler': route_event,
            },
            {
                'topics': [KafkaTopics.TICKET_CREATED],
                'group_id': 'custora-ticket-workers',
                'handler': route_event,
            },
            {
                'topics': [KafkaTopics.AGENT_EXECUTION_COMPLETED],
                'group_id': 'custora-agent-execution-workers',
                'handler': route_event,
            },
        ]

        # Create consumers
        for config in consumer_configs:
            try:
                consumer = await create_consumer(
                    topics=config['topics'],
                    group_id=config['group_id'],
                    handler=config['handler'],
                    enable_auto_commit=False,  # Manual commit for reliability
                )
                self.consumers.append(consumer)

                logger.info(f"[OK] Consumer created", extra={
                    'topics': config['topics'],
                    'group_id': config['group_id'],
                })

            except Exception as e:
                logger.error(f"Failed to create consumer: {e}", extra={
                    'topics': config['topics'],
                }, exc_info=True)

    async def _start_consumption(self) -> None:
        """Start consumption tasks for all consumers."""

        for consumer in self.consumers:
            # Create task for batch consumption
            task = asyncio.create_task(
                consumer.consume_batch(timeout_ms=10000),
                name=f"consumer-{consumer.group_id}"
            )
            self.tasks.append(task)

            logger.info(f"[OK] Consumption task started", extra={
                'group_id': consumer.group_id,
                'topics': consumer.topics,
            })

    async def stop(self) -> None:
        """
        Stop worker service gracefully.
        Stops all consumers and waits for tasks to complete.
        """
        try:
            logger.info("=" * 70)
            logger.info("Worker Service - Shutting Down")
            logger.info("=" * 70)

            self._should_stop = True

            # Stop all consumers
            for consumer in self.consumers:
                try:
                    await consumer.stop()
                    logger.info(f"[OK] Consumer stopped", extra={
                        'group_id': consumer.group_id,
                    })
                except Exception as e:
                    logger.error(f"Error stopping consumer: {e}", exc_info=True)

            # Cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()

            # Wait for tasks to complete
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)
                logger.info("[OK] All consumption tasks stopped")

            # Close database
            await close_db_pool()
            logger.info("[OK] Database pool closed")

            logger.info("=" * 70)
            logger.info("[OK] Worker Service Shutdown Complete")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

    async def run(self) -> None:
        """
        Run worker service.
        Starts service and waits for shutdown signal.
        """
        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()

        def signal_handler():
            logger.info("Received shutdown signal")
            asyncio.create_task(self.stop())

        # Register signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

        # Start service
        await self.start()

        # Wait for shutdown
        try:
            while not self._should_stop:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Worker service cancelled")


async def main():
    """Main entry point for worker service."""

    # Setup logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        environment=settings.ENVIRONMENT
    )

    # Check if Kafka is enabled
    if not settings.KAFKA_ENABLED:
        logger.error("Kafka is disabled in settings. Cannot start worker service.")
        logger.error("Set KAFKA_ENABLED=true in .env file")
        return

    # Create and run worker service
    service = WorkerService()

    try:
        await service.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Worker service error: {e}", exc_info=True)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
