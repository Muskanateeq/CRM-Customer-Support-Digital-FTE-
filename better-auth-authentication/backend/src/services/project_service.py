"""
Project Service

Business logic for project management including:
- Project CRUD operations
- Project status management
- User project access
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.project import Project, ProjectCreate, ProjectUpdate, ProjectPublic


class ProjectService:
    """Service for managing projects."""

    @staticmethod
    async def create_project(
        user_id: str,
        project_data: ProjectCreate,
        session: AsyncSession,
    ) -> ProjectPublic:
        """
        Create a new project.

        Args:
            user_id: User ID from JWT token (project owner)
            project_data: Project creation data
            session: Database session

        Returns:
            Created project
        """
        project = Project(
            user_id=user_id,
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status="active",
        )

        session.add(project)
        await session.commit()
        await session.refresh(project)

        return ProjectPublic(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    @staticmethod
    async def get_user_projects(
        user_id: str,
        session: AsyncSession,
        status: Optional[str] = None,
    ) -> List[ProjectPublic]:
        """
        Get all projects for a user.

        Args:
            user_id: User ID
            session: Database session
            status: Optional status filter (active, completed, archived)

        Returns:
            List of projects ordered by creation time (newest first)
        """
        query = select(Project).where(Project.user_id == user_id)

        if status:
            query = query.where(Project.status == status)

        query = query.order_by(Project.created_at.desc())

        result = await session.execute(query)
        projects = result.scalars().all()

        return [
            ProjectPublic(
                id=project.id,
                user_id=project.user_id,
                name=project.name,
                description=project.description,
                start_date=project.start_date,
                end_date=project.end_date,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            for project in projects
        ]

    @staticmethod
    async def get_project_by_id(
        project_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> Optional[ProjectPublic]:
        """
        Get project by ID.

        Only returns project if user owns it.

        Args:
            project_id: Project ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            Project or None if not found/unauthorized
        """
        result = await session.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            return None

        return ProjectPublic(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    @staticmethod
    async def update_project(
        project_id: int,
        user_id: str,
        project_data: ProjectUpdate,
        session: AsyncSession,
    ) -> Optional[ProjectPublic]:
        """
        Update a project.

        Only the project owner can update it.

        Args:
            project_id: Project ID
            user_id: User ID (for authorization)
            project_data: Updated project data
            session: Database session

        Returns:
            Updated project or None if not found/unauthorized
        """
        result = await session.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            return None

        # Update fields
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        if project_data.start_date is not None:
            project.start_date = project_data.start_date
        if project_data.end_date is not None:
            project.end_date = project_data.end_date
        if project_data.status is not None:
            project.status = project_data.status

        await session.commit()
        await session.refresh(project)

        return ProjectPublic(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    @staticmethod
    async def delete_project(
        project_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """
        Delete a project.

        Only the project owner can delete it.

        Args:
            project_id: Project ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            True if deleted, False if not found/unauthorized
        """
        result = await session.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            return False

        await session.delete(project)
        await session.commit()

        return True
