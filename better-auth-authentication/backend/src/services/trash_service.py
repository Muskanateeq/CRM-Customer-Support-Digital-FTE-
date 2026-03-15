"""
Trash Service Layer

Business logic for managing soft-deleted tasks (trash/recycle bin).
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.task import Task, TaskPublic
from src.services.task_service import TaskService


class TrashService:
    """Service class for trash/recycle bin operations"""

    @staticmethod
    async def get_deleted_tasks(
        user_id: str,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskPublic]:
        """
        Get all soft-deleted tasks for a user.

        Args:
            user_id: User ID from JWT token
            session: Database session
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            List of deleted tasks
        """
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.isnot(None)
            )
        ).order_by(Task.deleted_at.desc()).limit(limit).offset(offset)

        result = await session.execute(query)
        tasks = result.scalars().all()

        # Build response with tags
        tasks_public = []
        for task in tasks:
            tags = await TaskService._get_task_tags(task.id, session)
            tasks_public.append(
                TaskPublic(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    priority=task.priority,
                    due_date=task.due_date,
                    due_time=task.due_time,
                    recurrence_pattern=task.recurrence_pattern,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    tags=tags,
                )
            )

        return tasks_public

    @staticmethod
    async def restore_task(
        task_id: int,
        user_id: str,
        session: AsyncSession
    ) -> Optional[TaskPublic]:
        """
        Restore a soft-deleted task.

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            Restored task if found and owned by user, None otherwise
        """
        # Get deleted task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                    Task.deleted_at.isnot(None)
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Restore task - clear deleted_at timestamp
        task.deleted_at = None
        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)

        # Get tags for response
        tags = await TaskService._get_task_tags(task.id, session)

        # Log activity
        from src.services.activity_service import ActivityService
        await ActivityService.log_activity(
            user_id=user_id,
            activity_type="restored",
            title="Task Restored",
            description=f"Restored task: {task.title}",
            meta={"task_id": task_id, "task_name": task.title},
            session=session
        )

        return TaskPublic(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            due_date=task.due_date,
            due_time=task.due_time,
            recurrence_pattern=task.recurrence_pattern,
            created_at=task.created_at,
            updated_at=task.updated_at,
            tags=tags,
        )

    @staticmethod
    async def permanent_delete_task(
        task_id: int,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Permanently delete a task from trash.

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            True if task was permanently deleted, False if not found
        """
        # Get deleted task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                    Task.deleted_at.isnot(None)
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return False

        # Permanently delete task and its associations
        from src.models.task_tag import TaskTag
        from sqlalchemy import delete

        # Delete task_tags first
        await session.execute(
            delete(TaskTag).where(TaskTag.task_id == task_id)
        )

        # Delete task
        await session.delete(task)
        await session.commit()

        return True

    @staticmethod
    async def empty_trash(
        user_id: str,
        session: AsyncSession
    ) -> int:
        """
        Permanently delete all tasks in trash for a user.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            Number of tasks permanently deleted
        """
        # Get all deleted tasks
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.isnot(None)
                )
            )
        )
        tasks = result.scalars().all()

        count = 0
        for task in tasks:
            # Delete task_tags
            from src.models.task_tag import TaskTag
            from sqlalchemy import delete
            await session.execute(
                delete(TaskTag).where(TaskTag.task_id == task.id)
            )

            # Delete task
            await session.delete(task)
            count += 1

        await session.commit()
        return count
