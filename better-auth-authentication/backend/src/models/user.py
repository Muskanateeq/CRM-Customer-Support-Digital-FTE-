"""
User Model

SQLModel for user authentication and profile management.
Managed by Better Auth but defined here for database schema.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, func


class User(SQLModel, table=True):
    """
    User model for authentication.

    This model is managed by Better Auth on the frontend,
    but we define it here for database schema and backend queries.

    Note: Better Auth uses camelCase column names (createdAt, updatedAt, emailVerified)
    and does NOT store password_hash in the user table.
    """
    __tablename__ = "user"

    id: str = Field(
        sa_column=Column(String(255), primary_key=True),
        description="User ID (UUID from Better Auth)"
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True),
        description="User email address"
    )
    emailVerified: Optional[bool] = Field(
        default=None,
        sa_column=Column("emailVerified", nullable=True),
        description="Email verification status"
    )
    name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
        description="User display name"
    )
    image: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
        description="User profile image URL"
    )
    createdAt: datetime = Field(
        sa_column=Column(
            "createdAt",
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Account creation timestamp"
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            "updatedAt",
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Last update timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "emailVerified": True,
                "image": None,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }


class UserPublic(SQLModel):
    """
    Public user model for API responses.

    Matches Better Auth schema with camelCase field names.
    """
    id: str
    email: str
    name: Optional[str] = None
    emailVerified: Optional[bool] = None
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
