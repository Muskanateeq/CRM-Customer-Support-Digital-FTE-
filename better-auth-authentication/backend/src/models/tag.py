"""
Tag Model

SQLModel for user-specific tags/categories.
Each user can create custom tags to organize their tasks.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, UniqueConstraint
from sqlalchemy import TIMESTAMP, ForeignKey, func


class Tag(SQLModel, table=True):
    """
    Tag model for task categorization.

    Each tag belongs to a specific user and can be applied to multiple tasks.
    Tag names must be unique per user.
    """
    __tablename__ = "tags"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Tag ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who owns this tag"
    )
    name: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Tag name (e.g., Work, Home, Personal)"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Tag creation timestamp"
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Work",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class TagPublic(SQLModel):
    """
    Public tag model for API responses.

    Excludes internal fields and includes only user-facing data.
    """
    id: int
    name: str
    created_at: datetime


class TagCreate(SQLModel):
    """
    Schema for creating a new tag.

    User ID is extracted from JWT token, not from request.
    """
    name: str = Field(
        min_length=1,
        max_length=50,
        description="Tag name"
    )


class TagUpdate(SQLModel):
    """
    Schema for updating a tag.

    Currently only name can be updated.
    """
    name: str = Field(
        min_length=1,
        max_length=50,
        description="New tag name"
    )
