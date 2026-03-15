"""
TaskDependency Model

SQLModel for managing task dependencies.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, UniqueConstraint, CheckConstraint, func


class TaskDependency(SQLModel, table=True):
    """
    TaskDependency model for managing task dependencies.

    Defines relationships where one task must complete before another can start.
    """
    __tablename__ = "task_dependencies"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Dependency ID (auto-increment)"
    )
    predecessor_task_id: int = Field(
        sa_column=Column(ForeignKey("tasks.id"), nullable=False, index=True),
        description="Task that must complete first"
    )
    successor_task_id: int = Field(
        sa_column=Column(ForeignKey("tasks.id"), nullable=False, index=True),
        description="Task that depends on predecessor"
    )
    dependency_type: str = Field(
        default="finish_to_start",
        sa_column=Column(String(20), nullable=False),
        description="Dependency type: finish_to_start"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Dependency creation timestamp"
    )

    __table_args__ = (
        UniqueConstraint("predecessor_task_id", "successor_task_id", name="unique_dependency"),
        CheckConstraint("predecessor_task_id != successor_task_id", name="no_self_dependency"),
    )


class TaskDependencyCreate(SQLModel):
    """Schema for creating a task dependency."""
    predecessor_task_id: int = Field(description="Task that must complete first")
    successor_task_id: int = Field(description="Task that depends on predecessor")
    dependency_type: str = Field(
        default="finish_to_start",
        description="Dependency type: finish_to_start"
    )


class TaskDependencyPublic(SQLModel):
    """Public task dependency model for API responses."""
    id: int
    predecessor_task_id: int
    successor_task_id: int
    dependency_type: str
    created_at: datetime
