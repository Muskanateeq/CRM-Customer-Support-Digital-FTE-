"""
Notification Model

SQLModel for user notifications.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, ForeignKey, func


class Notification(SQLModel, table=True):
    """
    Notification model for user notifications.

    Tracks various types of notifications: task updates, mentions, assignments, reminders.
    """
    __tablename__ = "notifications"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Notification ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who receives this notification"
    )
    type: str = Field(
        sa_column=Column(String(50), nullable=False, index=True),
        description="Notification type: task_update, mention, assignment, reminder"
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Notification content/message"
    )
    related_item_type: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
        description="Type of related item: task, comment, project"
    )
    related_item_id: Optional[int] = Field(
        default=None,
        description="ID of related item"
    )
    read: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Whether notification has been read"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Notification creation timestamp"
    )


class NotificationCreate(SQLModel):
    """Schema for creating a notification."""
    type: str = Field(description="Notification type")
    content: str = Field(description="Notification content")
    related_item_type: Optional[str] = Field(
        default=None,
        description="Type of related item"
    )
    related_item_id: Optional[int] = Field(
        default=None,
        description="ID of related item"
    )


class NotificationPublic(SQLModel):
    """Public notification model for API responses."""
    id: int
    user_id: str
    type: str
    content: str
    related_item_type: Optional[str] = None
    related_item_id: Optional[int] = None
    read: bool
    created_at: datetime
