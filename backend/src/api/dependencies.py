"""
Custora Customer Success FTE - API Dependencies
FastAPI dependency injection for database, logging, etc.
"""

from fastapi import Request, HTTPException, status
from typing import Optional
import logging

from src.database.client import get_db_pool
from src.utils.logging import set_correlation_id, get_correlation_id

logger = logging.getLogger(__name__)


async def get_db():
    """
    Dependency for database connection pool.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db = Depends(get_db)):
            async with db.acquire() as conn:
                result = await conn.fetch("SELECT * FROM table")
    """
    try:
        pool = get_db_pool()
        return pool
    except RuntimeError as e:
        logger.error(f"Database pool not available: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )


async def setup_correlation_id(request: Request):
    """
    Dependency to setup correlation ID for request tracking.

    Checks for existing correlation ID in headers, or creates new one.
    """
    correlation_id = request.headers.get('X-Correlation-ID')
    if not correlation_id:
        correlation_id = set_correlation_id()
    else:
        set_correlation_id(correlation_id)

    return correlation_id


async def verify_api_key(request: Request) -> Optional[str]:
    """
    Dependency for API key verification (optional, for future use).

    Usage:
        @app.get("/protected")
        async def protected(api_key = Depends(verify_api_key)):
            return {"message": "Authorized"}
    """
    api_key = request.headers.get('X-API-Key')

    # For now, we don't enforce API keys
    # In production, you would validate against a database or config

    return api_key


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.

    Handles X-Forwarded-For header for proxied requests.
    """
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'
