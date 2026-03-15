"""
Conversation Model

SQLModel for storing chat conversations.
Each user can have multiple conversations.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Relationship
from sqlalchemy import TIMESTAMP, ForeignKey, func


class Conversation(SQLModel, table=True):
    """
    Conversation model for storing chat sessions.

    Each conversation belongs to a specific user and contains multiple messages.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Conversation ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), nullable=False, index=True),
        description="User ID who owns this conversation (from Better Auth JWT)"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            index=True
        ),
        description="Conversation last update timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class ConversationPublic(SQLModel):
    """
    Public conversation model for API responses.
    """
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0  # Number of messages in conversation


class ConversationCreate(SQLModel):
    """
    Schema for creating a new conversation.
    User ID is extracted from JWT token, not from request.
    """
    pass  # No fields needed, user_id comes from JWT


class ConversationList(SQLModel):
    """
    Schema for listing conversations.
    """
    conversations: List[ConversationPublic]
    total: int
