"""
Task Service Layer

Business logic for task operations including:
- CRUD operations
- Search, filter, and sort
- Tag associations
- Ownership validation
- Recurring task handling
"""

from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from sqlmodel import col

from src.models.task import Task, TaskCreate, TaskUpdate, TaskPublic
from src.models.tag import Tag
from src.models.task_tag import TaskTag


class TaskService:
    """Service class for task operations"""

    @staticmethod
    async def create_task(
        user_id: str,
        task_data: TaskCreate,
        session: AsyncSession
    ) -> TaskPublic:
        """
        Create a new task for the user.

        Args:
            user_id: User ID from JWT token
            task_data: Task creation data
            session: Database session

        Returns:
            Created task with tags
        """
        # Create task
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            due_date=task_data.due_date,
            due_time=task_data.due_time,
            recurrence_pattern=task_data.recurrence_pattern,
            completed=False,
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Associate tags
        if task_data.tag_ids:
            for tag_id in task_data.tag_ids:
                # Verify tag belongs to user
                tag_result = await session.execute(
                    select(Tag).where(
                        and_(Tag.id == tag_id, Tag.user_id == user_id)
                    )
                )
                tag = tag_result.scalar_one_or_none()

                if tag:
                    task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                    session.add(task_tag)

            await session.commit()

        # Get tags for response
        tags = await TaskService._get_task_tags(task.id, session)

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
    async def get_user_tasks(
        user_id: str,
        session: AsyncSession,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
        due_date_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[TaskPublic]:
        """
        Get all tasks for a user with optional filters and sorting.

        Args:
            user_id: User ID from JWT token
            session: Database session
            search: Search keyword (matches title and description)
            status: Filter by status (all, pending, completed)
            priority: Filter by priority (high, medium, low)
            tag_ids: Filter by tag IDs
            due_date_filter: Filter by due date (overdue, today, week, month, none)
            sort_by: Sort field (created_at, due_date, priority, title)
            sort_order: Sort order (asc, desc)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of tasks with tags
        """
        # Build query
        query = select(Task).where(Task.user_id == user_id)

        # Exclude soft-deleted tasks
        query = query.where(Task.deleted_at.is_(None))

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern),
                )
            )

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        # Apply priority filter
        if priority:
            query = query.where(Task.priority == priority)

        # Apply due date filter
        if due_date_filter:
            today = date.today()
            if due_date_filter == "overdue":
                query = query.where(
                    and_(Task.due_date.isnot(None), Task.due_date < today)
                )
            elif due_date_filter == "today":
                query = query.where(Task.due_date == today)
            elif due_date_filter == "week":
                from datetime import timedelta
                week_end = today + timedelta(days=7)
                query = query.where(
                    and_(
                        Task.due_date.isnot(None),
                        Task.due_date >= today,
                        Task.due_date <= week_end,
                    )
                )
            elif due_date_filter == "month":
                from datetime import timedelta
                month_end = today + timedelta(days=30)
                query = query.where(
                    and_(
                        Task.due_date.isnot(None),
                        Task.due_date >= today,
                        Task.due_date <= month_end,
                    )
                )
            elif due_date_filter == "none":
                query = query.where(Task.due_date.is_(None))

        # Apply tag filter
        if tag_ids:
            # Get tasks that have ALL specified tags
            for tag_id in tag_ids:
                query = query.where(
                    Task.id.in_(
                        select(TaskTag.task_id).where(TaskTag.tag_id == tag_id)
                    )
                )

        # Apply sorting
        if sort_by == "created_at":
            sort_col = Task.created_at
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())
        elif sort_by == "due_date":
            # Special handling for due_date: overdue first, then upcoming, nulls last
            from sqlalchemy import case, func
            today = date.today()

            # Create a case statement to prioritize overdue tasks
            priority_order = case(
                (Task.due_date < today, 1),  # Overdue tasks first
                (Task.due_date >= today, 2),  # Upcoming tasks second
                else_=3  # No due date last
            )

            if sort_order == "asc":
                # Overdue first, then upcoming in chronological order
                query = query.order_by(priority_order.asc(), Task.due_date.asc().nullslast())
            else:
                # Still show overdue first, but reverse the chronological order within each group
                query = query.order_by(priority_order.asc(), Task.due_date.desc().nullslast())
        elif sort_by == "priority":
            # Custom priority sorting: high > medium > low
            from sqlalchemy import case
            sort_col = case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
            )
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())
        elif sort_by == "title":
            sort_col = Task.title
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())
        else:
            sort_col = Task.created_at
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
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
    async def get_task_by_id(
        task_id: int,
        user_id: str,
        session: AsyncSession
    ) -> Optional[TaskPublic]:
        """
        Get a single task by ID.

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            Task with tags if found and owned by user, None otherwise
        """
        result = await session.execute(
            select(Task).where(
                and_(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None))
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return None

        tags = await TaskService._get_task_tags(task.id, session)

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
    async def update_task(
        task_id: int,
        user_id: str,
        task_data: TaskUpdate,
        session: AsyncSession
    ) -> Optional[TaskPublic]:
        """
        Update a task.

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            task_data: Task update data
            session: Database session

        Returns:
            Updated task with tags if found and owned by user, None otherwise
        """
        # Get task
        result = await session.execute(
            select(Task).where(
                and_(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None))
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
        if task_data.due_time is not None:
            task.due_time = task_data.due_time
        if task_data.recurrence_pattern is not None:
            task.recurrence_pattern = task_data.recurrence_pattern

        task.updated_at = datetime.utcnow()

        # Update tags if provided
        if task_data.tag_ids is not None:
            # Remove existing tags
            await session.execute(
                delete(TaskTag).where(TaskTag.task_id == task_id)
            )

            # Add new tags
            for tag_id in task_data.tag_ids:
                # Verify tag belongs to user
                tag_result = await session.execute(
                    select(Tag).where(
                        and_(Tag.id == tag_id, Tag.user_id == user_id)
                    )
                )
                tag = tag_result.scalar_one_or_none()

                if tag:
                    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
                    session.add(task_tag)

        await session.commit()
        await session.refresh(task)

        # Get tags for response
        tags = await TaskService._get_task_tags(task.id, session)

        # Log activity
        from src.services.activity_service import ActivityService
        changes = []
        if task_data.title is not None:
            changes.append(f"Title updated")
        if task_data.priority is not None:
            changes.append(f"Priority changed to {task_data.priority}")
        if task_data.due_date is not None:
            changes.append(f"Due date updated")

        await ActivityService.log_activity(
            user_id=user_id,
            activity_type="updated",
            title="Task Updated",
            description=f"Updated task: {task.title}",
            meta={
                "task_id": task_id,
                "task_name": task.title,
                "changes": changes
            },
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
    async def delete_task(
        task_id: int,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Soft delete a task (mark as deleted, don't remove from database).

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            True if task was deleted, False if not found or not owned by user
        """
        # Get task
        result = await session.execute(
            select(Task).where(
                and_(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None))
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return False

        # Soft delete - set deleted_at timestamp
        task.deleted_at = datetime.utcnow()
        await session.commit()

        # Log activity
        from src.services.activity_service import ActivityService
        await ActivityService.log_activity(
            user_id=user_id,
            activity_type="deleted",
            title="Task Deleted",
            description=f"Deleted task: {task.title}",
            meta={"task_id": task_id, "task_name": task.title},
            session=session
        )

        return True

    @staticmethod
    async def toggle_completion(
        task_id: int,
        user_id: str,
        completed: bool,
        session: AsyncSession
    ) -> Optional[TaskPublic]:
        """
        Toggle task completion status.

        If task is recurring and being marked complete, create next occurrence.

        Args:
            task_id: Task ID
            user_id: User ID from JWT token (for ownership validation)
            completed: New completion status
            session: Database session

        Returns:
            Updated task with tags if found and owned by user, None otherwise
        """
        # Get task
        result = await session.execute(
            select(Task).where(
                and_(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None))
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update completion status
        task.completed = completed
        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        # Handle recurring task: create next occurrence when marked complete
        if completed and task.recurrence_pattern and task.due_date:
            await TaskService._create_next_recurring_task(task, user_id, session)

        # Get tags for response
        tags = await TaskService._get_task_tags(task.id, session)

        # Log activity
        from src.services.activity_service import ActivityService
        activity_type = "completed" if completed else "uncompleted"
        title = "Task Completed" if completed else "Task Uncompleted"
        description = f"{'Completed' if completed else 'Marked incomplete'} task: {task.title}"

        await ActivityService.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=description,
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
    async def _get_task_tags(task_id: int, session: AsyncSession) -> List[dict]:
        """
        Get tags for a task.

        Args:
            task_id: Task ID
            session: Database session

        Returns:
            List of tag objects with id, name, user_id, created_at
        """
        result = await session.execute(
            select(Tag)
            .join(TaskTag, TaskTag.tag_id == Tag.id)
            .where(TaskTag.task_id == task_id)
        )
        tags = result.scalars().all()
        return [
            {
                "id": tag.id,
                "name": tag.name,
                "user_id": tag.user_id,
                "created_at": tag.created_at.isoformat() if tag.created_at else None,
            }
            for tag in tags
        ]

    @staticmethod
    async def _create_next_recurring_task(
        completed_task: Task,
        user_id: str,
        session: AsyncSession
    ) -> None:
        """
        Create next occurrence of a recurring task.

        Args:
            completed_task: The task that was just completed
            user_id: User ID
            session: Database session
        """
        if not completed_task.recurrence_pattern or not completed_task.due_date:
            return

        pattern = completed_task.recurrence_pattern
        pattern_type = pattern.get("type", "").lower()
        interval = pattern.get("interval", 1)

        # Calculate next due date based on pattern type
        next_due_date = None
        current_due = completed_task.due_date

        if pattern_type == "daily":
            next_due_date = current_due + timedelta(days=interval)

        elif pattern_type == "weekly":
            next_due_date = current_due + timedelta(weeks=interval)

        elif pattern_type == "monthly":
            # Add months (approximate with 30 days per month)
            next_due_date = current_due + timedelta(days=30 * interval)

        elif pattern_type == "custom":
            # Custom pattern with specific days
            days = pattern.get("days", [])
            if days:
                # For custom patterns, add interval weeks
                next_due_date = current_due + timedelta(weeks=interval)

        else:
            # Unknown pattern type, default to weekly
            next_due_date = current_due + timedelta(weeks=1)

        if not next_due_date:
            return

        # Check if there's an end date
        end_date = pattern.get("end_date")
        if end_date:
            # Parse end_date if it's a string
            if isinstance(end_date, str):
                try:
                    from dateutil import parser
                    end_date = parser.parse(end_date).date()
                except:
                    end_date = None

            if end_date and next_due_date > end_date:
                # Don't create task if past end date
                return

        # Get tags from completed task
        tag_result = await session.execute(
            select(TaskTag.tag_id).where(TaskTag.task_id == completed_task.id)
        )
        tag_ids = [row[0] for row in tag_result.all()]

        # Create new task with same properties but new due date
        new_task = Task(
            user_id=user_id,
            title=completed_task.title,
            description=completed_task.description,
            priority=completed_task.priority,
            due_date=next_due_date,
            due_time=completed_task.due_time,
            recurrence_pattern=completed_task.recurrence_pattern,
            completed=False,
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        # Associate same tags
        for tag_id in tag_ids:
            task_tag = TaskTag(task_id=new_task.id, tag_id=tag_id)
            session.add(task_tag)

        await session.commit()
