"""
Task Model

SQLModel for task management with support for:
- Basic features: CRUD operations, completion status
- Intermediate features: priorities, tags, search, filter, sort
- Advanced features: due dates, recurring tasks, reminders
"""

from typing import Optional, List
from datetime import datetime, date, time
from sqlmodel import SQLModel, Field, Column, String, Text, Relationship
from sqlalchemy import TIMESTAMP, Date, Time, CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB


class Task(SQLModel, table=True):
    """
    Task model with all fields for Basic + Intermediate + Advanced features.

    Each task belongs to a specific user and can have multiple tags.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Task ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who owns this task (from Better Auth)"
    )
    title: str = Field(
        sa_column=Column(String(200), nullable=False),
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Task description (optional, max 1000 characters)"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Task completion status"
    )
    priority: str = Field(
        default="medium",
        sa_column=Column(String(10), nullable=False, index=True),
        description="Task priority: high, medium, or low"
    )
    due_date: Optional[date] = Field(
        default=None,
        sa_column=Column(Date, nullable=True, index=True),
        description="Task due date (optional)"
    )
    due_time: Optional[time] = Field(
        default=None,
        sa_column=Column(Time, nullable=True),
        description="Task due time (optional)"
    )
    recurrence_pattern: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Recurrence pattern for recurring tasks (JSON)"
    )
    project_id: Optional[int] = Field(
        default=None,
        sa_column=Column(ForeignKey("projects.id"), nullable=True, index=True),
        description="Project ID this task belongs to (optional)"
    )
    assigned_to: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=True, index=True),
        description="User ID this task is assigned to (from Better Auth)"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            index=True
        ),
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Task last update timestamp"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP, nullable=True, index=True),
        description="Soft delete timestamp (NULL if not deleted)"
    )

    __table_args__ = (
        CheckConstraint(
            "priority IN ('high', 'medium', 'low')",
            name='ck_task_priority'
        ),
        CheckConstraint(
            "length(title) >= 1 AND length(title) <= 200",
            name='ck_task_title_length'
        ),
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "due_date": "2024-01-15",
                "due_time": "14:00:00",
                "recurrence_pattern": {
                    "type": "weekly",
                    "interval": 1,
                    "days": ["monday", "wednesday"]
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class TaskPublic(SQLModel):
    """
    Public task model for API responses.

    Includes all task fields plus associated tags.
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: str
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence_pattern: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    tags: List[dict] = []  # List of tag objects with id, name, user_id, created_at


class TaskCreate(SQLModel):
    """
    Schema for creating a new task.

    User ID is extracted from JWT token, not from request.
    """
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )
    priority: str = Field(
        default="medium",
        description="Task priority: high, medium, or low"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (optional)"
    )
    due_time: Optional[time] = Field(
        default=None,
        description="Task due time (optional)"
    )
    recurrence_pattern: Optional[dict] = Field(
        default=None,
        description="Recurrence pattern (optional)"
    )
    tag_ids: List[int] = Field(
        default=[],
        description="List of tag IDs to associate with task"
    )


class TaskUpdate(SQLModel):
    """
    Schema for updating a task.

    All fields are optional - only provided fields will be updated.
    """
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Task priority"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date"
    )
    due_time: Optional[time] = Field(
        default=None,
        description="Task due time"
    )
    recurrence_pattern: Optional[dict] = Field(
        default=None,
        description="Recurrence pattern"
    )
    tag_ids: Optional[List[int]] = Field(
        default=None,
        description="List of tag IDs"
    )


class TaskCompletionToggle(SQLModel):
    """
    Schema for toggling task completion status.
    """
    completed: bool = Field(
        description="New completion status"
    )
