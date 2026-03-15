"""
TaskTag Junction Model

SQLModel for many-to-many relationship between tasks and tags.
Allows tasks to have multiple tags and tags to be applied to multiple tasks.
"""

from typing import Optional
from sqlmodel import SQLModel, Field, Column, Integer
from sqlalchemy import ForeignKey


class TaskTag(SQLModel, table=True):
    """
    TaskTag junction table for many-to-many relationship.

    Links tasks with tags, allowing:
    - One task to have multiple tags
    - One tag to be applied to multiple tasks
    """
    __tablename__ = "task_tags"

    task_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tasks.id"), primary_key=True),
        description="Task ID"
    )
    tag_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tags.id"), primary_key=True),
        description="Tag ID"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "tag_id": 2
            }
        }
