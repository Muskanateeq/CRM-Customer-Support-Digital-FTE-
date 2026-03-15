"""
Authentication Schemas

Pydantic schemas for authentication requests and responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas import BaseSchema, TimestampSchema


class RegisterRequest(BaseSchema):
    """
    User registration request schema.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User display name"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Password must contain:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        return v


class LoginRequest(BaseSchema):
    """
    User login request schema.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseSchema):
    """
    JWT token response schema.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class AuthResponse(BaseSchema):
    """
    Authentication response with user data and token.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User profile data")


class UserResponse(TimestampSchema):
    """
    User profile response schema.
    """
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")


class RefreshTokenRequest(BaseSchema):
    """
    Token refresh request schema.
    """
    refresh_token: str = Field(..., description="Refresh token")


class LogoutResponse(BaseSchema):
    """
    Logout response schema.
    """
    success: bool = Field(True, description="Logout success status")
    message: str = Field(default="Logged out successfully", description="Success message")
