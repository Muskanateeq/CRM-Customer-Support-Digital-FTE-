"""
Activity Model

SQLModel for tracking user activities and actions.
Stores all task-related operations for history and audit trail.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB


class Activity(SQLModel, table=True):
    """
    Activity model for tracking user actions.

    Stores all task operations (create, update, delete, complete)
    for history tracking and audit trail.
    """
    __tablename__ = "activities"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Activity ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who performed this action"
    )
    type: str = Field(
        sa_column=Column(String(50), nullable=False, index=True),
        description="Activity type (created, updated, deleted, completed, etc.)"
    )
    title: str = Field(
        sa_column=Column(String(200), nullable=False),
        description="Activity title (e.g., 'Task Created', 'Task Deleted')"
    )
    description: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Activity description (e.g., 'Created task: Meeting')"
    )
    meta: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Additional metadata (task_id, task_name, changes, etc.)"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Activity timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "created",
                "title": "Task Created",
                "description": "Created task: Meeting with team",
                "meta": {
                    "task_id": 123,
                    "task_name": "Meeting with team",
                    "priority": "high"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class ActivityPublic(SQLModel):
    """
    Public activity model for API responses.
    """
    id: int
    type: str
    title: str
    description: str
    meta: Optional[dict] = None
    created_at: datetime


class ActivityCreate(SQLModel):
    """
    Schema for creating a new activity.
    User ID is extracted from JWT token.
    """
    type: str = Field(
        min_length=1,
        max_length=50,
        description="Activity type"
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Activity title"
    )
    description: str = Field(
        min_length=1,
        description="Activity description"
    )
    meta: Optional[dict] = Field(
        default=None,
        description="Additional metadata"
    )
