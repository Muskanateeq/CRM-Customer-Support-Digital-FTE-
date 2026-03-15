"""
Authentication API Endpoints

NOTE: User registration, login, and logout are handled by Better Auth on the frontend.
This module only provides endpoints for getting current user information.

Better Auth endpoints (handled by Next.js):
- POST /api/auth/sign-up (registration)
- POST /api/auth/sign-in/email (login)
- POST /api/auth/sign-out (logout)
- GET /api/auth/session (get session)
- GET /api/auth/jwks (JWKS for JWT verification)
- POST /api/auth/token (get JWT token)
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.database.client import get_db_connection
from src.models.user import UserPublic
from src.api.deps import get_current_user_id
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user",
    description="Get profile of currently authenticated user"
)
async def get_current_user(
    user_id: str = Depends(get_current_user_id)
) -> UserPublic:
    """
    Get current user profile.

    Requires valid Better Auth JWT token in Authorization header.

    Returns user profile data (excludes password).

    Example:
        GET /api/v1/auth/me
        Authorization: Bearer <jwt_token>

        Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "name": "John Doe",
            "emailVerified": true,
            "image": null,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
    """
    try:
        async with get_db_connection() as conn:
            # Query user from database
            row = await conn.fetchrow(
                """
                SELECT
                    id,
                    email,
                    name,
                    "emailVerified",
                    image,
                    "createdAt",
                    "updatedAt"
                FROM "user"
                WHERE id = $1
                """,
                user_id
            )

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Return public user data
            return UserPublic(
                id=row['id'],
                email=row['email'],
                name=row['name'],
                emailVerified=row['emailVerified'],
                image=row['image'],
                createdAt=row['createdAt'],
                updatedAt=row['updatedAt']
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.get(
    "/health",
    summary="Auth system health check",
    description="Check if authentication system is working"
)
async def auth_health_check():
    """
    Health check for authentication system.

    Returns:
        Status message indicating auth system is operational
    """
    return {
        "status": "healthy",
        "message": "Authentication system operational",
        "auth_provider": "Better Auth",
        "jwt_verification": "JWKS"
    }
