"""
Team Service Layer

Business logic for team operations including:
- Team CRUD operations
- Member management
- Team invitations
- Ownership validation
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlmodel import col
import secrets

from src.models.team import Team, TeamCreate, TeamUpdate, TeamPublic
from src.models.team_member import TeamMember
from src.models.team_invitation import TeamInvitation


class TeamService:
    """Service class for team operations"""

    @staticmethod
    async def create_team(
        user_id: str,
        team_data: TeamCreate,
        session: AsyncSession
    ) -> TeamPublic:
        """
        Create a new team.

        Args:
            user_id: User ID from JWT token (team creator)
            team_data: Team creation data
            session: Database session

        Returns:
            Created team
        """
        # Create team
        team = Team(
            name=team_data.name,
            description=team_data.description,
            creator_id=user_id,
        )

        session.add(team)
        await session.commit()
        await session.refresh(team)

        # Add creator as admin member
        member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role='admin',
        )
        session.add(member)
        await session.commit()

        return TeamPublic(
            id=team.id,
            name=team.name,
            description=team.description,
            creator_id=team.creator_id,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    async def get_user_teams(
        user_id: str,
        session: AsyncSession
    ) -> List[TeamPublic]:
        """
        Get all teams where user is a member.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            List of teams
        """
        # Get team IDs where user is a member
        member_result = await session.execute(
            select(TeamMember.team_id).where(TeamMember.user_id == user_id)
        )
        team_ids = [row[0] for row in member_result.all()]

        if not team_ids:
            return []

        # Get teams
        result = await session.execute(
            select(Team).where(col(Team.id).in_(team_ids))
        )
        teams = result.scalars().all()

        return [
            TeamPublic(
                id=team.id,
                name=team.name,
                description=team.description,
                creator_id=team.creator_id,
                created_at=team.created_at,
                updated_at=team.updated_at,
            )
            for team in teams
        ]

    @staticmethod
    async def get_team_by_id(
        team_id: int,
        user_id: str,
        session: AsyncSession
    ) -> Optional[TeamPublic]:
        """
        Get team by ID if user is a member.

        Args:
            team_id: Team ID
            user_id: User ID from JWT token
            session: Database session

        Returns:
            Team or None
        """
        # Verify user is a member
        member_result = await session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id
                )
            )
        )
        member = member_result.scalar_one_or_none()

        if not member:
            return None

        # Get team
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return None

        return TeamPublic(
            id=team.id,
            name=team.name,
            description=team.description,
            creator_id=team.creator_id,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    async def update_team(
        team_id: int,
        user_id: str,
        team_data: TeamUpdate,
        session: AsyncSession
    ) -> Optional[TeamPublic]:
        """
        Update team (admin only).

        Args:
            team_id: Team ID
            user_id: User ID from JWT token
            team_data: Team update data
            session: Database session

        Returns:
            Updated team or None
        """
        # Verify user is admin
        member_result = await session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id,
                    TeamMember.role == 'admin'
                )
            )
        )
        member = member_result.scalar_one_or_none()

        if not member:
            return None

        # Get team
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return None

        # Update fields
        if team_data.name is not None:
            team.name = team_data.name
        if team_data.description is not None:
            team.description = team_data.description

        await session.commit()
        await session.refresh(team)

        return TeamPublic(
            id=team.id,
            name=team.name,
            description=team.description,
            creator_id=team.creator_id,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    async def delete_team(
        team_id: int,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Delete team (creator only).

        Args:
            team_id: Team ID
            user_id: User ID from JWT token
            session: Database session

        Returns:
            True if deleted, False otherwise
        """
        # Get team and verify creator
        result = await session.execute(
            select(Team).where(
                and_(
                    Team.id == team_id,
                    Team.creator_id == user_id
                )
            )
        )
        team = result.scalar_one_or_none()

        if not team:
            return False

        await session.delete(team)
        await session.commit()

        return True

    @staticmethod
    async def get_team_members(
        team_id: int,
        user_id: str,
        session: AsyncSession
    ) -> Optional[List[dict]]:
        """
        Get team members (members only).

        Args:
            team_id: Team ID
            user_id: User ID from JWT token
            session: Database session

        Returns:
            List of members or None
        """
        # Verify user is a member
        member_result = await session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id
                )
            )
        )
        member = member_result.scalar_one_or_none()

        if not member:
            return None

        # Get all members
        result = await session.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        )
        members = result.scalars().all()

        return [
            {
                'id': m.id,
                'team_id': m.team_id,
                'user_id': m.user_id,
                'role': m.role,
                'joined_at': m.joined_at.isoformat(),
            }
            for m in members
        ]

    @staticmethod
    async def invite_member(
        team_id: int,
        user_id: str,
        email: str,
        session: AsyncSession
    ) -> Optional[dict]:
        """
        Create team invitation (admin only).

        Args:
            team_id: Team ID
            user_id: User ID from JWT token (inviter)
            email: Email to invite
            session: Database session

        Returns:
            Invitation details or None
        """
        # Verify user is admin
        member_result = await session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id,
                    TeamMember.role == 'admin'
                )
            )
        )
        member = member_result.scalar_one_or_none()

        if not member:
            return None

        # Generate invitation token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)

        # Create invitation
        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            inviter_id=user_id,
            status='pending',
            token=token,
            expires_at=expires_at,
        )

        session.add(invitation)
        await session.commit()
        await session.refresh(invitation)

        return {
            'id': invitation.id,
            'team_id': invitation.team_id,
            'email': invitation.email,
            'status': invitation.status,
            'token': invitation.token,
            'expires_at': invitation.expires_at.isoformat(),
            'created_at': invitation.created_at.isoformat(),
        }
