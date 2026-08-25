"""Application startup migrations required by background services."""

import logging
from pathlib import Path

from src.database.client import get_db_connection

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_CHANNEL_SECURITY_MIGRATION = (
    _BACKEND_ROOT / "migrations" / "004_channel_security_jobs.sql"
)


async def ensure_channel_jobs_schema() -> None:
    """Create the durable channel queue before its worker is started.

    The SQL migration is idempotent, so this is safe on every application
    startup and also covers Render services that do not run pre-deploy hooks.
    """
    migration_sql = _CHANNEL_SECURITY_MIGRATION.read_text(encoding="utf-8")

    async with get_db_connection() as connection:
        await connection.execute(migration_sql)

    logger.info("[OK] Durable channel job schema is ready")
