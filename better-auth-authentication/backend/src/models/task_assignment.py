"""
TaskAssignment Model

SQLModel for tracking task assignments.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, func


class TaskAssignment(SQLModel, table=True):
    """
    TaskAssignment model for tracking when tasks are assigned to users.

    Maintains history of task assignments.
    """
    __tablename__ = "task_assignments"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Assignment ID (auto-increment)"
    )
    task_id: int = Field(
        sa_column=Column(ForeignKey("tasks.id"), nullable=False, index=True),
        description="Task ID"
    )
    assignee_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who is assigned the task"
    )
    assigner_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False),
        description="User ID who assigned the task"
    )
    assigned_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Assignment timestamp"
    )


class TaskAssignmentCreate(SQLModel):
    """Schema for creating a task assignment."""
    assignee_id: str = Field(description="User ID to assign task to")


class TaskAssignmentPublic(SQLModel):
    """Public task assignment model for API responses."""
    id: int
    task_id: int
    assignee_id: str
    assigner_id: str
    assigned_at: datetime
