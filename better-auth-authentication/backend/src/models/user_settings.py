"""
User Settings Model

SQLModel for user preferences and settings.
"""

from typing import Optional
from datetime import datetime, time
from sqlmodel import SQLModel, Field, Column, String, Boolean, Integer
from sqlalchemy import TIMESTAMP, TIME, func


class UserSettings(SQLModel, table=True):
    """
    User settings model for preferences.

    Stores user-specific preferences for notifications, appearance, and tasks.
    """
    __tablename__ = "user_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True),
        description="User ID (foreign key to user table)"
    )

    # Notification preferences
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    browser_notifications: bool = Field(default=True, description="Enable browser notifications")
    task_reminders: bool = Field(default=True, description="Enable task due date reminders")
    dnd_enabled: bool = Field(default=False, description="Do Not Disturb mode enabled")
    dnd_start: Optional[time] = Field(
        default=None,
        sa_column=Column(TIME, nullable=True),
        description="DND start time"
    )
    dnd_end: Optional[time] = Field(
        default=None,
        sa_column=Column(TIME, nullable=True),
        description="DND end time"
    )

    # Appearance preferences
    theme: str = Field(default="dark", description="UI theme (light/dark)")
    font_size: str = Field(default="medium", description="Font size (small/medium/large)")
    view_mode: str = Field(default="comfortable", description="View mode (compact/comfortable/spacious)")

    # Task preferences
    default_priority: str = Field(default="medium", description="Default task priority")
    default_sort: str = Field(default="created_date", description="Default task sort")
    show_completed: bool = Field(default=True, description="Show completed tasks by default")

    # Language preference
    language: str = Field(default="en", description="UI language code")

    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Settings creation timestamp"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Last update timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email_notifications": True,
                "browser_notifications": True,
                "task_reminders": True,
                "theme": "dark",
                "font_size": "medium",
                "default_priority": "medium"
            }
        }


class UserSettingsUpdate(SQLModel):
    """Schema for updating user settings"""
    email_notifications: Optional[bool] = None
    browser_notifications: Optional[bool] = None
    task_reminders: Optional[bool] = None
    dnd_enabled: Optional[bool] = None
    dnd_start: Optional[time] = None
    dnd_end: Optional[time] = None
    theme: Optional[str] = None
    font_size: Optional[str] = None
    view_mode: Optional[str] = None
    default_priority: Optional[str] = None
    default_sort: Optional[str] = None
    show_completed: Optional[bool] = None
    language: Optional[str] = None


class UserProfileUpdate(SQLModel):
    """Schema for updating user profile"""
    name: Optional[str] = None


class ChangePasswordRequest(SQLModel):
    """Schema for password change request"""
    current_password: str
    new_password: str
