"""
Authentication Service

Business logic for user authentication, registration, and token management.
"""

import uuid
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from src.models.user import User, UserPublic
from src.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from src.utils.security import hash_password, verify_password
from src.utils.jwt import create_access_token, create_refresh_token
from src.config import settings


class AuthService:
    """
    Authentication service for user management and token operations.
    """

    @staticmethod
    async def register_user(
        data: RegisterRequest,
        session: AsyncSession
    ) -> AuthResponse:
        """
        Register a new user.

        NOTE: This function is deprecated. Better Auth handles user registration.
        This is kept for backward compatibility but should not be used.

        Args:
            data: Registration request data
            session: Database session

        Returns:
            AuthResponse with user data and JWT token

        Raises:
            HTTPException: Registration is handled by Better Auth
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User registration is handled by Better Auth. Use the Better Auth sign-up flow."
        )

    @staticmethod
    async def login_user(
        data: LoginRequest,
        session: AsyncSession
    ) -> AuthResponse:
        """
        Authenticate user and generate JWT token.

        NOTE: This function is deprecated. Better Auth handles user login.
        This is kept for backward compatibility but should not be used.

        Args:
            data: Login request data
            session: Database session

        Returns:
            AuthResponse with user data and JWT token

        Raises:
            HTTPException: Login is handled by Better Auth
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User login is handled by Better Auth. Use the Better Auth sign-in flow."
        )

    @staticmethod
    async def get_user_by_id(
        user_id: str,
        session: AsyncSession
    ) -> Optional[UserPublic]:
        """
        Get user by ID.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            UserPublic if found, None otherwise
        """
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return UserPublic(
                id=user.id,
                email=user.email,
                name=user.name,
                emailVerified=user.emailVerified,
                image=user.image,
                createdAt=user.createdAt,
                updatedAt=user.updatedAt
            )

        return None

    @staticmethod
    async def get_current_user(
        user_id: str,
        session: AsyncSession
    ) -> UserPublic:
        """
        Get current authenticated user.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            UserPublic

        Raises:
            HTTPException: If user not found
        """
        user = await AuthService.get_user_by_id(user_id, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
