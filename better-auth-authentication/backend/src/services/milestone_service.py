"""
Milestone Service

Business logic for project milestone management.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.milestone import Milestone, MilestoneCreate, MilestoneUpdate, MilestonePublic
from src.models.project import Project


class MilestoneService:
    """Service for managing project milestones."""

    @staticmethod
    async def create_milestone(
        project_id: int,
        user_id: str,
        milestone_data: MilestoneCreate,
        session: AsyncSession,
    ) -> Optional[MilestonePublic]:
        """
        Create a new milestone for a project.

        Args:
            project_id: Project ID
            user_id: User ID (for authorization)
            milestone_data: Milestone creation data
            session: Database session

        Returns:
            Created milestone or None if project not found/unauthorized
        """
        # Verify project exists and user owns it
        project_result = await session.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
        )
        project = project_result.scalar_one_or_none()

        if not project:
            return None

        # Create milestone
        milestone = Milestone(
            project_id=project_id,
            name=milestone_data.name,
            description=milestone_data.description,
            date=milestone_data.date,
            completed=False,
        )

        session.add(milestone)
        await session.commit()
        await session.refresh(milestone)

        return MilestonePublic(
            id=milestone.id,
            project_id=milestone.project_id,
            name=milestone.name,
            description=milestone.description,
            date=milestone.date,
            completed=milestone.completed,
            created_at=milestone.created_at,
        )

    @staticmethod
    async def get_project_milestones(
        project_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> Optional[List[MilestonePublic]]:
        """
        Get all milestones for a project.

        Args:
            project_id: Project ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            List of milestones or None if project not found/unauthorized
        """
        # Verify project exists and user owns it
        project_result = await session.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
        )
        project = project_result.scalar_one_or_none()

        if not project:
            return None

        # Get milestones
        result = await session.execute(
            select(Milestone)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.date.asc())
        )
        milestones = result.scalars().all()

        return [
            MilestonePublic(
                id=milestone.id,
                project_id=milestone.project_id,
                name=milestone.name,
                description=milestone.description,
                date=milestone.date,
                completed=milestone.completed,
                created_at=milestone.created_at,
            )
            for milestone in milestones
        ]

    @staticmethod
    async def update_milestone(
        milestone_id: int,
        user_id: str,
        milestone_data: MilestoneUpdate,
        session: AsyncSession,
    ) -> Optional[MilestonePublic]:
        """
        Update a milestone.

        Args:
            milestone_id: Milestone ID
            user_id: User ID (for authorization)
            milestone_data: Updated milestone data
            session: Database session

        Returns:
            Updated milestone or None if not found/unauthorized
        """
        # Get milestone and verify ownership through project
        result = await session.execute(
            select(Milestone, Project)
            .join(Project, Milestone.project_id == Project.id)
            .where(
                and_(
                    Milestone.id == milestone_id,
                    Project.user_id == user_id,
                )
            )
        )
        row = result.first()

        if not row:
            return None

        milestone = row[0]

        # Update fields
        if milestone_data.name is not None:
            milestone.name = milestone_data.name
        if milestone_data.description is not None:
            milestone.description = milestone_data.description
        if milestone_data.date is not None:
            milestone.date = milestone_data.date
        if milestone_data.completed is not None:
            milestone.completed = milestone_data.completed

        await session.commit()
        await session.refresh(milestone)

        return MilestonePublic(
            id=milestone.id,
            project_id=milestone.project_id,
            name=milestone.name,
            description=milestone.description,
            date=milestone.date,
            completed=milestone.completed,
            created_at=milestone.created_at,
        )

    @staticmethod
    async def delete_milestone(
        milestone_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """
        Delete a milestone.

        Args:
            milestone_id: Milestone ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            True if deleted, False if not found/unauthorized
        """
        # Get milestone and verify ownership through project
        result = await session.execute(
            select(Milestone, Project)
            .join(Project, Milestone.project_id == Project.id)
            .where(
                and_(
                    Milestone.id == milestone_id,
                    Project.user_id == user_id,
                )
            )
        )
        row = result.first()

        if not row:
            return False

        milestone = row[0]

        await session.delete(milestone)
        await session.commit()

        return True
