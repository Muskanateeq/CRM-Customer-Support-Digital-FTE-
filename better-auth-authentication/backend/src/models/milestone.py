"""
Milestone Model

SQLModel for project milestones.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, Date, ForeignKey, func


class Milestone(SQLModel, table=True):
    """
    Milestone model for tracking project milestones.

    Milestones mark significant points in a project timeline.
    """
    __tablename__ = "milestones"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Milestone ID (auto-increment)"
    )
    project_id: int = Field(
        sa_column=Column(ForeignKey("projects.id"), nullable=False, index=True),
        description="Project ID this milestone belongs to"
    )
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Milestone name"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Milestone description (optional)"
    )
    date: datetime = Field(
        sa_column=Column(Date, nullable=False),
        description="Milestone target date"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Milestone completion status"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Milestone creation timestamp"
    )


class MilestoneCreate(SQLModel):
    """Schema for creating a milestone."""
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Milestone name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Milestone description (optional)"
    )
    date: datetime = Field(description="Milestone target date")


class MilestoneUpdate(SQLModel):
    """Schema for updating a milestone."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Milestone name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Milestone description"
    )
    date: Optional[datetime] = Field(
        default=None,
        description="Milestone target date"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Milestone completion status"
    )


class MilestonePublic(SQLModel):
    """Public milestone model for API responses."""
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    date: datetime
    completed: bool
    created_at: datetime
