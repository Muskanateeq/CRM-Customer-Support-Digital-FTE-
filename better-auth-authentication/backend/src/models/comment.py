"""
Comment Model

SQLModel for task comments and mentions.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB


class Comment(SQLModel, table=True):
    """
    Comment model for task discussions.

    Supports @mentions for notifying team members.
    """
    __tablename__ = "comments"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Comment ID (auto-increment)"
    )
    task_id: int = Field(
        sa_column=Column(ForeignKey("tasks.id"), nullable=False, index=True),
        description="Task ID this comment belongs to"
    )
    author_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who wrote this comment"
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Comment content"
    )
    mentions: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="List of user IDs mentioned in this comment"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Comment creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Comment last update timestamp"
    )


class CommentCreate(SQLModel):
    """Schema for creating a comment."""
    content: str = Field(
        min_length=1,
        max_length=2000,
        description="Comment content"
    )
    mentions: Optional[List[str]] = Field(
        default=None,
        description="List of user IDs to mention"
    )


class CommentUpdate(SQLModel):
    """Schema for updating a comment."""
    content: str = Field(
        min_length=1,
        max_length=2000,
        description="Updated comment content"
    )


class CommentPublic(SQLModel):
    """Public comment model for API responses."""
    id: int
    task_id: int
    author_id: str
    content: str
    mentions: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
