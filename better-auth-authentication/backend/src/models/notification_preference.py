"""
NotificationPreference Model

SQLModel for user notification preferences.
"""

from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB


class NotificationPreference(SQLModel, table=True):
    """
    NotificationPreference model for managing user notification settings.

    Controls which notification types and channels are enabled for each user.
    """
    __tablename__ = "notification_preferences"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Preference ID (auto-increment)"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, unique=True, index=True),
        description="User ID (one preference record per user)"
    )
    enabled_types: Dict = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Enabled notification types: {task_update: true, mention: true, ...}"
    )
    enabled_channels: Dict = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Enabled notification channels: {in_app: true, browser: true, email: false}"
    )
    dnd_start_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb start hour (0-23)"
    )
    dnd_end_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb end hour (0-23)"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Preference creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Preference last update timestamp"
    )


class NotificationPreferenceCreate(SQLModel):
    """Schema for creating notification preferences."""
    enabled_types: Dict = Field(
        default={
            "task_update": True,
            "mention": True,
            "assignment": True,
            "reminder": True
        },
        description="Enabled notification types"
    )
    enabled_channels: Dict = Field(
        default={
            "in_app": True,
            "browser": True,
            "email": False
        },
        description="Enabled notification channels"
    )
    dnd_start_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb start hour (0-23)"
    )
    dnd_end_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb end hour (0-23)"
    )


class NotificationPreferenceUpdate(SQLModel):
    """Schema for updating notification preferences."""
    enabled_types: Optional[Dict] = Field(
        default=None,
        description="Enabled notification types"
    )
    enabled_channels: Optional[Dict] = Field(
        default=None,
        description="Enabled notification channels"
    )
    dnd_start_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb start hour (0-23)"
    )
    dnd_end_hour: Optional[int] = Field(
        default=None,
        description="Do Not Disturb end hour (0-23)"
    )


class NotificationPreferencePublic(SQLModel):
    """Public notification preference model for API responses."""
    id: int
    user_id: str
    enabled_types: Dict
    enabled_channels: Dict
    dnd_start_hour: Optional[int] = None
    dnd_end_hour: Optional[int] = None
    created_at: datetime
    updated_at: datetime
