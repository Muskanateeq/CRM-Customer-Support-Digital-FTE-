"""
Message Model

SQLModel for storing chat messages within conversations.
Each message belongs to a conversation and has a role (user or assistant).
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, ForeignKey, CheckConstraint, func


class Message(SQLModel, table=True):
    """
    Message model for storing individual chat messages.

    Each message belongs to a conversation and has a role (user or assistant).
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Message ID (auto-increment)"
    )
    conversation_id: int = Field(
        sa_column=Column(ForeignKey("conversations.id"), nullable=False, index=True),
        description="Conversation ID this message belongs to"
    )
    user_id: str = Field(
        sa_column=Column(String(255), nullable=False, index=True),
        description="User ID who owns this message (from Better Auth JWT)"
    )
    role: str = Field(
        sa_column=Column(String(20), nullable=False),
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Message content"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Message creation timestamp"
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name='ck_message_role'
        ),
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class MessagePublic(SQLModel):
    """
    Public message model for API responses.
    """
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class MessageCreate(SQLModel):
    """
    Schema for creating a new message.
    """
    conversation_id: int
    role: str = Field(
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        min_length=1,
        max_length=10000,
        description="Message content"
    )


class MessageList(SQLModel):
    """
    Schema for listing messages.
    """
    messages: list[MessagePublic]
    total: int
    has_more: bool
