"""
User Model

SQLModel for user authentication and profile management.
Managed by Better Auth but defined here for database schema.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """
    User model for authentication.

    This model is managed by Better Auth on the frontend,
    but we define it here for database schema and backend queries.

    Note: Better Auth uses camelCase column names (createdAt, updatedAt, emailVerified)
    """
    id: str
    email: str
    emailVerified: Optional[bool] = None
    name: Optional[str] = None
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class UserPublic(BaseModel):
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
