"""
Worker Pool - Manages Multiple Worker Instances
Enables horizontal scaling by running multiple worker processes
"""

import asyncio
import multiprocessing
from typing import List
from datetime import datetime

from src.config import settings
from src.utils.logging import setup_logging, get_logger
from src.workers.service import WorkerService

logger = get_logger(__name__)


class WorkerPool:
    """
    Worker pool that manages multiple worker processes.
    Each process runs a WorkerService instance.
    """

    def __init__(self, num_workers: int = None):
        """
        Initialize worker pool.

        Args:
            num_workers: Number of worker processes (default: CPU count)
        """
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.processes: List[multiprocessing.Process] = []

    def start(self) -> None:
        """Start all worker processes."""

        logger.info("=" * 70)
        logger.info("Custora Worker Pool - Starting")
        logger.info("=" * 70)
        logger.info(f"Number of workers: {self.num_workers}")
        logger.info(f"CPU count: {multiprocessing.cpu_count()}")
        logger.info("=" * 70)

        # Create and start worker processes
        for i in range(self.num_workers):
            process = multiprocessing.Process(
                target=self._run_worker,
                args=(i,),
                name=f"worker-{i}"
            )
            process.start()
            self.processes.append(process)

            logger.info(f"[OK] Worker process started", extra={
                'worker_id': i,
                'pid': process.pid,
            })

        logger.info("=" * 70)
        logger.info(f"[OK] Worker Pool Started - {self.num_workers} Workers Running")
        logger.info("=" * 70)

    def _run_worker(self, worker_id: int) -> None:
        """
        Run worker service in a separate process.

        Args:
            worker_id: Worker identifier
        """
        # Setup logging for this process
        setup_logging(
            log_level=settings.LOG_LEVEL,
            environment=settings.ENVIRONMENT
        )

        logger.info(f"Worker {worker_id} starting", extra={
            'worker_id': worker_id,
            'pid': multiprocessing.current_process().pid,
        })

        # Run worker service
        asyncio.run(self._run_worker_service(worker_id))

    async def _run_worker_service(self, worker_id: int) -> None:
        """
        Run worker service async.

        Args:
            worker_id: Worker identifier
        """
        service = WorkerService()

        try:
            await service.run()
        except Exception as e:
            logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
        finally:
            await service.stop()

    def stop(self) -> None:
        """Stop all worker processes gracefully."""

        logger.info("=" * 70)
        logger.info("Worker Pool - Shutting Down")
        logger.info("=" * 70)

        # Terminate all processes
        for i, process in enumerate(self.processes):
            if process.is_alive():
                logger.info(f"Stopping worker {i}", extra={
                    'worker_id': i,
                    'pid': process.pid,
                })
                process.terminate()

        # Wait for processes to terminate
        for i, process in enumerate(self.processes):
            process.join(timeout=10)

            if process.is_alive():
                logger.warning(f"Worker {i} did not terminate, killing", extra={
                    'worker_id': i,
                    'pid': process.pid,
                })
                process.kill()
            else:
                logger.info(f"[OK] Worker {i} stopped", extra={
                    'worker_id': i,
                })

        logger.info("=" * 70)
        logger.info("[OK] Worker Pool Shutdown Complete")
        logger.info("=" * 70)

    def run(self) -> None:
        """
        Run worker pool.
        Starts all workers and waits for keyboard interrupt.
        """
        try:
            self.start()

            # Wait for keyboard interrupt
            logger.info("Worker pool running. Press Ctrl+C to stop.")

            # Keep main process alive
            for process in self.processes:
                process.join()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop()


def main():
    """Main entry point for worker pool."""

    # Setup logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        environment=settings.ENVIRONMENT
    )

    # Check if Kafka is enabled
    if not settings.KAFKA_ENABLED:
        logger.error("Kafka is disabled in settings. Cannot start worker pool.")
        logger.error("Set KAFKA_ENABLED=true in .env file")
        return

    # Get number of workers from settings or use CPU count
    num_workers = getattr(settings, 'WORKER_POOL_SIZE', None)

    # Create and run worker pool
    pool = WorkerPool(num_workers=num_workers)
    pool.run()


if __name__ == "__main__":
    main()
