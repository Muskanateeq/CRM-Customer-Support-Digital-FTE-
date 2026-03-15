"""
Project Model

SQLModel for project management features.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, Date, ForeignKey, func


class Project(SQLModel, table=True):
    """
    Project model for organizing tasks into projects.

    Projects have start/end dates and track overall progress.
    """
    __tablename__ = "projects"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Project ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who owns this project"
    )
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Project name"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Project description (optional)"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(Date, nullable=True),
        description="Project start date (optional)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(Date, nullable=True),
        description="Project end date (optional)"
    )
    status: str = Field(
        default="active",
        sa_column=Column(String(20), nullable=False, index=True),
        description="Project status: active, completed, archived"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Project creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Project last update timestamp"
    )


class ProjectCreate(SQLModel):
    """Schema for creating a new project."""
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Project name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Project description (optional)"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Project start date (optional)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Project end date (optional)"
    )


class ProjectUpdate(SQLModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Project name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Project description"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Project start date"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Project end date"
    )
    status: Optional[str] = Field(
        default=None,
        description="Project status: active, completed, archived"
    )


class ProjectPublic(SQLModel):
    """Public project model for API responses."""
    id: int
    user_id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime
