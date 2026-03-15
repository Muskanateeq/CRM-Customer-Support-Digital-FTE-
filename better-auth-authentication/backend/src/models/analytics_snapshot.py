"""
AnalyticsSnapshot Model

SQLModel for storing analytics data snapshots.
"""

from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, Date, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB


class AnalyticsSnapshot(SQLModel, table=True):
    """
    AnalyticsSnapshot model for storing daily analytics data.

    Captures point-in-time statistics for performance and trend analysis.
    """
    __tablename__ = "analytics_snapshots"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Snapshot ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID"
    )
    date: datetime = Field(
        sa_column=Column(Date, nullable=False, index=True),
        description="Snapshot date"
    )
    tasks_created: int = Field(
        default=0,
        description="Number of tasks created on this date"
    )
    tasks_completed: int = Field(
        default=0,
        description="Number of tasks completed on this date"
    )
    average_completion_time_hours: Optional[float] = Field(
        default=None,
        description="Average time to complete tasks (in hours)"
    )
    priority_distribution: Dict = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Task distribution by priority: {high: 5, medium: 10, low: 3}"
    )
    tag_distribution: Dict = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Task distribution by tag: {work: 8, personal: 5}"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Snapshot creation timestamp"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="unique_user_date_snapshot"),
    )


class AnalyticsSnapshotCreate(SQLModel):
    """Schema for creating an analytics snapshot."""
    date: datetime = Field(description="Snapshot date")
    tasks_created: int = Field(default=0, description="Tasks created")
    tasks_completed: int = Field(default=0, description="Tasks completed")
    average_completion_time_hours: Optional[float] = Field(
        default=None,
        description="Average completion time"
    )
    priority_distribution: Dict = Field(description="Priority distribution")
    tag_distribution: Dict = Field(description="Tag distribution")


class AnalyticsSnapshotPublic(SQLModel):
    """Public analytics snapshot model for API responses."""
    id: int
    user_id: str
    date: datetime
    tasks_created: int
    tasks_completed: int
    average_completion_time_hours: Optional[float] = None
    priority_distribution: Dict
    tag_distribution: Dict
    created_at: datetime
