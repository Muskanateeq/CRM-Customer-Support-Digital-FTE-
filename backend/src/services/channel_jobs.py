"""Durable database-backed queue for inbound Gmail and WhatsApp work."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Optional

from src.config import settings
from src.database.client import get_db_connection
from src.utils.logging import get_logger

logger = get_logger(__name__)

ChannelJobHandler = Callable[[Dict[str, Any]], Awaitable[None]]

_handlers: Dict[str, ChannelJobHandler] = {}
_worker_task: Optional[asyncio.Task] = None
_stop_event: Optional[asyncio.Event] = None


def register_channel_job_handler(channel: str, handler: ChannelJobHandler) -> None:
    """Register the processor for a durable channel job type."""
    _handlers[channel] = handler


async def enqueue_channel_job(
    channel: str,
    external_message_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Persist a job exactly once for a channel/external-message pair."""
    if not external_message_id:
        raise ValueError("external_message_id is required")

    payload_json = json.dumps(payload)

    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO channel_jobs (channel, external_message_id, payload)
            VALUES ($1, $2, $3::jsonb)
            ON CONFLICT (channel, external_message_id) DO NOTHING
            RETURNING id, status
            """,
            channel,
            external_message_id,
            payload_json,
        )

        if row:
            return {"job_id": str(row["id"]), "status": row["status"], "created": True}

        existing = await conn.fetchrow(
            """
            SELECT id, status
            FROM channel_jobs
            WHERE channel = $1 AND external_message_id = $2
            """,
            channel,
            external_message_id,
        )

        return {
            "job_id": str(existing["id"]),
            "status": existing["status"],
            "created": False,
        }


async def _claim_next_job() -> Optional[Dict[str, Any]]:
    """Atomically claim one pending or stale job."""
    async with get_db_connection() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                SELECT id, channel, external_message_id, payload, attempts, max_attempts
                FROM channel_jobs
                WHERE attempts < max_attempts
                  AND (
                    (status = 'pending' AND available_at <= NOW())
                    OR (
                      status = 'processing'
                      AND locked_at < NOW() - ($1 * INTERVAL '1 second')
                    )
                  )
                ORDER BY created_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
                """,
                settings.CHANNEL_JOB_STALE_AFTER_SECONDS,
            )

            if not row:
                return None

            claimed = await conn.fetchrow(
                """
                UPDATE channel_jobs
                SET status = 'processing',
                    attempts = attempts + 1,
                    locked_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, channel, external_message_id, payload, attempts, max_attempts
                """,
                row["id"],
            )

    job = dict(claimed)
    if isinstance(job["payload"], str):
        job["payload"] = json.loads(job["payload"])
    return job


async def _complete_job(job_id: Any) -> None:
    async with get_db_connection() as conn:
        await conn.execute(
            """
            UPDATE channel_jobs
            SET status = 'completed',
                completed_at = NOW(),
                locked_at = NULL,
                last_error = NULL,
                updated_at = NOW()
            WHERE id = $1
            """,
            job_id,
        )


async def _fail_job(job: Dict[str, Any], error: Exception) -> None:
    terminal = job["attempts"] >= job["max_attempts"]
    status = "failed" if terminal else "pending"
    safe_error = str(error)[:2000]

    async with get_db_connection() as conn:
        await conn.execute(
            """
            UPDATE channel_jobs
            SET status = $2,
                last_error = $3,
                locked_at = NULL,
                available_at = CASE
                    WHEN $2 = 'pending'
                    THEN NOW() + (LEAST(POWER(2, attempts)::int, 300) * INTERVAL '1 second')
                    ELSE available_at
                END,
                updated_at = NOW()
            WHERE id = $1
            """,
            job["id"],
            status,
            safe_error,
        )

    logger.error(
        "Channel job failed",
        extra={
            "job_id": str(job["id"]),
            "channel": job["channel"],
            "attempt": job["attempts"],
            "terminal": terminal,
        },
    )


async def _run_worker() -> None:
    assert _stop_event is not None
    logger.info("Durable channel job worker started")

    while not _stop_event.is_set():
        try:
            job = await _claim_next_job()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Unable to claim a durable channel job")
            try:
                await asyncio.wait_for(
                    _stop_event.wait(),
                    timeout=settings.CHANNEL_JOB_POLL_INTERVAL_SECONDS,
                )
            except asyncio.TimeoutError:
                pass
            continue

        if not job:
            try:
                await asyncio.wait_for(
                    _stop_event.wait(),
                    timeout=settings.CHANNEL_JOB_POLL_INTERVAL_SECONDS,
                )
            except asyncio.TimeoutError:
                pass
            continue

        handler = _handlers.get(job["channel"])
        if not handler:
            await _fail_job(job, RuntimeError(f"No handler registered for {job['channel']}"))
            continue

        try:
            await handler(job["payload"])
            await _complete_job(job["id"])
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await _fail_job(job, exc)

    logger.info("Durable channel job worker stopped")


async def start_channel_job_worker() -> None:
    """Start one local worker task; database locking coordinates other instances."""
    global _worker_task, _stop_event

    if not settings.CHANNEL_JOB_WORKER_ENABLED or _worker_task is not None:
        return

    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_run_worker(), name="channel-job-worker")


async def stop_channel_job_worker() -> None:
    """Stop the local worker without discarding persisted jobs."""
    global _worker_task, _stop_event

    if _worker_task is None or _stop_event is None:
        return

    _stop_event.set()
    try:
        await asyncio.wait_for(_worker_task, timeout=10)
    except asyncio.TimeoutError:
        _worker_task.cancel()
        await asyncio.gather(_worker_task, return_exceptions=True)
    finally:
        _worker_task = None
        _stop_event = None
