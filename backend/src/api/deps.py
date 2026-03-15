"""
API Dependencies

Dependency injection functions for FastAPI endpoints.
Handles authentication, database sessions, and common dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utils.jwt import decode_better_auth_token
from src.utils.logging import get_logger

logger = get_logger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate user_id from JWT token.

    This dependency MUST be used on all protected endpoints to ensure:
    1. User is authenticated (valid JWT token)
    2. User ID is extracted from token (NOT from request parameters)
    3. User data isolation is enforced

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User ID extracted from valid JWT token

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Example:
        @app.get("/api/v1/tasks")
        async def get_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is guaranteed to be from validated JWT token
            tasks = await get_user_tasks(user_id)
            return tasks
    """
    token = credentials.credentials

    # Decode and validate Better Auth JWT token using JWKS
    payload = decode_better_auth_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id: Optional[str] = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Extract user_id from JWT token if present, otherwise return None.

    Use this for endpoints that work for both authenticated and unauthenticated users.

    Args:
        credentials: Optional HTTP Bearer token

    Returns:
        User ID if token is valid, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_better_auth_token(token)

    if payload is None:
        return None

    return payload.get("user_id")
