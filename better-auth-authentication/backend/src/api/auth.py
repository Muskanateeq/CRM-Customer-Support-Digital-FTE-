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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.models.user import User, UserPublic
from src.api.deps import get_current_user_id

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user",
    description="Get profile of currently authenticated user"
)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
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
    # Query user from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return public user data
    return UserPublic(
        id=user.id,
        email=user.email,
        name=user.name,
        emailVerified=user.emailVerified,
        image=user.image,
        createdAt=user.createdAt,
        updatedAt=user.updatedAt
    )


# Health check endpoint for auth system
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
