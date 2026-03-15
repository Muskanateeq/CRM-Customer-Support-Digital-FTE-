"""
CustomReport Model

SQLModel for user-generated analytics reports.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB


class CustomReport(SQLModel, table=True):
    """
    CustomReport model for storing user-generated analytics reports.

    Allows users to create custom reports with selected metrics and date ranges.
    """
    __tablename__ = "custom_reports"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Report ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID who created this report"
    )
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Report name"
    )
    metrics: List[str] = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Selected metrics: ['completion_rate', 'priority_distribution']"
    )
    date_range_start: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False),
        description="Report date range start"
    )
    date_range_end: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False),
        description="Report date range end"
    )
    shareable_token: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True, unique=True, index=True),
        description="Unique token for sharing report"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Report creation timestamp"
    )


class CustomReportCreate(SQLModel):
    """Schema for creating a custom report."""
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Report name"
    )
    metrics: List[str] = Field(
        description="Selected metrics for the report"
    )
    date_range_start: datetime = Field(description="Report date range start")
    date_range_end: datetime = Field(description="Report date range end")


class CustomReportPublic(SQLModel):
    """Public custom report model for API responses."""
    id: int
    user_id: str
    name: str
    metrics: List[str]
    date_range_start: datetime
    date_range_end: datetime
    shareable_token: Optional[str] = None
    created_at: datetime
