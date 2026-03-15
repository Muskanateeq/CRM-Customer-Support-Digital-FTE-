"""
Task Assignment Service

Business logic for task assignments and team member assignment.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.task_assignment import (
    TaskAssignment,
    TaskAssignmentCreate,
    TaskAssignmentPublic,
)
from src.models.task import Task


class TaskAssignmentService:
    """Service for managing task assignments."""

    @staticmethod
    async def assign_task(
        task_id: int,
        assignee_id: str,
        assigner_id: str,
        session: AsyncSession,
    ) -> Optional[TaskAssignmentPublic]:
        """
        Assign a task to a user.

        Args:
            task_id: Task ID to assign
            assignee_id: User ID to assign task to
            assigner_id: User ID who is assigning the task
            session: Database session

        Returns:
            Created assignment or None if task not found
        """
        # Verify task exists
        task_result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return None

        # Check if already assigned to this user
        existing_result = await session.execute(
            select(TaskAssignment).where(
                and_(
                    TaskAssignment.task_id == task_id,
                    TaskAssignment.assignee_id == assignee_id,
                )
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Already assigned, return existing assignment
            return TaskAssignmentPublic(
                id=existing.id,
                task_id=existing.task_id,
                assignee_id=existing.assignee_id,
                assigner_id=existing.assigner_id,
                assigned_at=existing.assigned_at,
            )

        # Create new assignment
        assignment = TaskAssignment(
            task_id=task_id,
            assignee_id=assignee_id,
            assigner_id=assigner_id,
        )

        session.add(assignment)
        await session.commit()
        await session.refresh(assignment)

        return TaskAssignmentPublic(
            id=assignment.id,
            task_id=assignment.task_id,
            assignee_id=assignment.assignee_id,
            assigner_id=assignment.assigner_id,
            assigned_at=assignment.assigned_at,
        )

    @staticmethod
    async def get_task_assignments(
        task_id: int,
        session: AsyncSession,
    ) -> List[TaskAssignmentPublic]:
        """
        Get all assignments for a task.

        Args:
            task_id: Task ID
            session: Database session

        Returns:
            List of assignments
        """
        result = await session.execute(
            select(TaskAssignment)
            .where(TaskAssignment.task_id == task_id)
            .order_by(TaskAssignment.assigned_at.desc())
        )
        assignments = result.scalars().all()

        return [
            TaskAssignmentPublic(
                id=assignment.id,
                task_id=assignment.task_id,
                assignee_id=assignment.assignee_id,
                assigner_id=assignment.assigner_id,
                assigned_at=assignment.assigned_at,
            )
            for assignment in assignments
        ]

    @staticmethod
    async def get_user_assignments(
        user_id: str,
        session: AsyncSession,
    ) -> List[TaskAssignmentPublic]:
        """
        Get all task assignments for a user.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            List of assignments
        """
        result = await session.execute(
            select(TaskAssignment)
            .where(TaskAssignment.assignee_id == user_id)
            .order_by(TaskAssignment.assigned_at.desc())
        )
        assignments = result.scalars().all()

        return [
            TaskAssignmentPublic(
                id=assignment.id,
                task_id=assignment.task_id,
                assignee_id=assignment.assignee_id,
                assigner_id=assignment.assigner_id,
                assigned_at=assignment.assigned_at,
            )
            for assignment in assignments
        ]

    @staticmethod
    async def unassign_task(
        task_id: int,
        assignee_id: str,
        session: AsyncSession,
    ) -> bool:
        """
        Unassign a task from a user.

        Args:
            task_id: Task ID
            assignee_id: User ID to unassign
            session: Database session

        Returns:
            True if unassigned, False if not found
        """
        result = await session.execute(
            select(TaskAssignment).where(
                and_(
                    TaskAssignment.task_id == task_id,
                    TaskAssignment.assignee_id == assignee_id,
                )
            )
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            return False

        await session.delete(assignment)
        await session.commit()

        return True
