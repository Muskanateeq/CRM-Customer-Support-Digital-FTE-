"""
TeamInvitation Model

SQLModel for team invitation management.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import TIMESTAMP, ForeignKey, func


class TeamInvitation(SQLModel, table=True):
    """
    TeamInvitation model for managing team invitations.

    Tracks pending, accepted, declined, and expired invitations.
    """
    __tablename__ = "team_invitations"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Invitation ID (auto-increment)"
    )
    team_id: int = Field(
        sa_column=Column(ForeignKey("teams.id"), nullable=False, index=True),
        description="Team ID"
    )
    email: str = Field(
        sa_column=Column(String(255), nullable=False, index=True),
        description="Email address of invitee"
    )
    inviter_id: str = Field(
        sa_column=Column(String(255), ForeignKey("user.id"), nullable=False),
        description="User ID who sent the invitation"
    )
    status: str = Field(
        default="pending",
        sa_column=Column(String(20), nullable=False),
        description="Invitation status: pending, accepted, declined, expired"
    )
    token: str = Field(
        sa_column=Column(String(255), nullable=False, unique=True, index=True),
        description="Unique invitation token"
    )
    expires_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False),
        description="Invitation expiration timestamp"
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now()
        ),
        description="Invitation creation timestamp"
    )


class TeamInvitationCreate(SQLModel):
    """Schema for creating a team invitation."""
    email: str = Field(
        description="Email address to invite"
    )


class TeamInvitationPublic(SQLModel):
    """Public team invitation model for API responses."""
    id: int
    team_id: int
    email: str
    inviter_id: str
    status: str
    expires_at: datetime
    created_at: datetime
