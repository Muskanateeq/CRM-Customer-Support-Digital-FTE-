"""
TeamMember Model

SQLModel for team membership management.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, UniqueConstraint, func


class TeamMember(SQLModel, table=True):
    """
    TeamMember model for managing team membership.

    Links users to teams with specific roles.
    """
    __tablename__ = "team_members"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Team member ID (auto-increment)"
    )
    team_id: int = Field(
        sa_column=Column(ForeignKey("teams.id"), nullable=False, index=True),
        description="Team ID"
    )
    user_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False, index=True),
        description="User ID"
    )
    role: str = Field(
        default="member",
        sa_column=Column(String(20), nullable=False),
        description="Member role: admin, member, or viewer"
    )
    joined_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Timestamp when user joined the team"
    )

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="unique_team_member"),
    )


class TeamMemberCreate(SQLModel):
    """Schema for adding a member to a team."""
    user_id: str = Field(description="User ID to add to team")
    role: str = Field(
        default="member",
        description="Member role: admin, member, or viewer"
    )


class TeamMemberUpdate(SQLModel):
    """Schema for updating a team member's role."""
    role: str = Field(description="New role: admin, member, or viewer")


class TeamMemberPublic(SQLModel):
    """Public team member model for API responses."""
    id: int
    team_id: int
    user_id: str
    role: str
    joined_at: datetime
