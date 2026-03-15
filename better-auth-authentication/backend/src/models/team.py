"""
Team Model

SQLModel for team collaboration features.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import TIMESTAMP, ForeignKey, func


class Team(SQLModel, table=True):
    """
    Team model for collaboration.

    Teams allow multiple users to work together on tasks.
    """
    __tablename__ = "teams"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Team ID (auto-increment)"
    )
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Team name"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Team description (optional)"
    )
    creator_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who created this team"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Team creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Team last update timestamp"
    )


class TeamCreate(SQLModel):
    """Schema for creating a new team."""
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Team name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Team description (optional)"
    )


class TeamUpdate(SQLModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Team name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Team description"
    )


class TeamPublic(SQLModel):
    """Public team model for API responses."""
    id: int
    name: str
    description: Optional[str] = None
    creator_id: str
    created_at: datetime
    updated_at: datetime
