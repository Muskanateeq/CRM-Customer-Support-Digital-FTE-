"""
Task Service Layer Tests

Tests for business logic in task service including:
- Recurring task logic
- Search and filter logic
- Data isolation
"""

import pytest
from datetime import date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.models.tag import Tag
from src.services.task_service import TaskService


class TestTaskServiceCreate:
    """Test task creation service logic"""

    @pytest.mark.asyncio
    async def test_create_task_basic(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test creating a basic task"""
        task_data = TaskCreate(
            title="Service Test Task",
            description="Test description",
            priority="high",
        )

        task = await TaskService.create_task(
            user_id=test_user.id,
            task_data=task_data,
            session=test_session
        )

        assert task.title == "Service Test Task"
        assert task.description == "Test description"
        assert task.priority == "high"
        assert task.completed is False
        assert task.id is not None

    @pytest.mark.asyncio
    async def test_create_task_with_tags(
        self, test_session: AsyncSession, test_user: User, test_tag: Tag
    ):
        """Test creating task with tags"""
        task_data = TaskCreate(
            title="Task with tags",
            priority="medium",
            tag_ids=[test_tag.id]
        )

        task = await TaskService.create_task(
            user_id=test_user.id,
            task_data=task_data,
            session=test_session
        )

        assert task.id is not None
        assert test_tag.name in task.tags


class TestTaskServiceRecurrence:
    """Test recurring task logic"""

    @pytest.mark.asyncio
    async def test_daily_recurrence_creates_next_day(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that daily recurrence creates task for next day"""
        # Create recurring task
        task = Task(
            user_id=test_user.id,
            title="Daily Task",
            priority="medium",
            completed=False,
            due_date=date(2026, 2, 7),
            due_time=time(9, 0),
            recurrence_pattern={
                "type": "daily",
                "interval": 1,
            }
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mark as complete (should trigger recurrence)
        updated_task = await TaskService.toggle_completion(
            task_id=task.id,
            user_id=test_user.id,
            completed=True,
            session=test_session
        )

        assert updated_task.completed is True

        # Check that new task was created
        result = await test_session.execute(
            select(Task).where(
                Task.user_id == test_user.id,
                Task.completed == False
            )
        )
        new_tasks = result.scalars().all()

        assert len(new_tasks) == 1
        new_task = new_tasks[0]
        assert new_task.title == "Daily Task"
        assert new_task.due_date == date(2026, 2, 8)  # Next day
        assert new_task.due_time == time(9, 0)

    @pytest.mark.asyncio
    async def test_weekly_recurrence_creates_next_week(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that weekly recurrence creates task for next week"""
        task = Task(
            user_id=test_user.id,
            title="Weekly Task",
            priority="high",
            completed=False,
            due_date=date(2026, 2, 7),
            recurrence_pattern={
                "type": "weekly",
                "interval": 1,
            }
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mark as complete
        await TaskService.toggle_completion(
            task_id=task.id,
            user_id=test_user.id,
            completed=True,
            session=test_session
        )

        # Check new task
        result = await test_session.execute(
            select(Task).where(
                Task.user_id == test_user.id,
                Task.completed == False
            )
        )
        new_tasks = result.scalars().all()

        assert len(new_tasks) == 1
        new_task = new_tasks[0]
        assert new_task.due_date == date(2026, 2, 14)  # Next week

    @pytest.mark.asyncio
    async def test_monthly_recurrence_creates_next_month(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that monthly recurrence creates task for next month"""
        task = Task(
            user_id=test_user.id,
            title="Monthly Task",
            priority="medium",
            completed=False,
            due_date=date(2026, 2, 7),
            recurrence_pattern={
                "type": "monthly",
                "interval": 1,
            }
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mark as complete
        await TaskService.toggle_completion(
            task_id=task.id,
            user_id=test_user.id,
            completed=True,
            session=test_session
        )

        # Check new task
        result = await test_session.execute(
            select(Task).where(
                Task.user_id == test_user.id,
                Task.completed == False
            )
        )
        new_tasks = result.scalars().all()

        assert len(new_tasks) == 1
        new_task = new_tasks[0]
        # Approximately 30 days later
        assert new_task.due_date >= date(2026, 3, 7)

    @pytest.mark.asyncio
    async def test_non_recurring_task_no_new_task(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that non-recurring task doesn't create new task"""
        task = Task(
            user_id=test_user.id,
            title="One-time Task",
            priority="low",
            completed=False,
            due_date=date(2026, 2, 7),
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mark as complete
        await TaskService.toggle_completion(
            task_id=task.id,
            user_id=test_user.id,
            completed=True,
            session=test_session
        )

        # Check that no new task was created
        result = await test_session.execute(
            select(Task).where(Task.user_id == test_user.id)
        )
        all_tasks = result.scalars().all()

        # Should only have the original task
        assert len(all_tasks) == 1
        assert all_tasks[0].completed is True


class TestTaskServiceSearch:
    """Test search and filter logic"""

    @pytest.mark.asyncio
    async def test_search_by_title(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test searching tasks by title"""
        # Create multiple tasks
        task1 = Task(user_id=test_user.id, title="Buy groceries", priority="medium", completed=False)
        task2 = Task(user_id=test_user.id, title="Call dentist", priority="high", completed=False)
        task3 = Task(user_id=test_user.id, title="Buy tickets", priority="low", completed=False)

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Search for "Buy"
        results = await TaskService.get_user_tasks(
            user_id=test_user.id,
            session=test_session,
            search="Buy"
        )

        assert len(results) == 2
        assert all("Buy" in task.title for task in results)

    @pytest.mark.asyncio
    async def test_filter_by_status(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test filtering tasks by completion status"""
        task1 = Task(user_id=test_user.id, title="Task 1", priority="medium", completed=True)
        task2 = Task(user_id=test_user.id, title="Task 2", priority="high", completed=False)
        task3 = Task(user_id=test_user.id, title="Task 3", priority="low", completed=False)

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Filter for pending tasks
        results = await TaskService.get_user_tasks(
            user_id=test_user.id,
            session=test_session,
            status="pending"
        )

        assert len(results) == 2
        assert all(not task.completed for task in results)

    @pytest.mark.asyncio
    async def test_sort_by_priority(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test sorting tasks by priority"""
        task1 = Task(user_id=test_user.id, title="Low priority", priority="low", completed=False)
        task2 = Task(user_id=test_user.id, title="High priority", priority="high", completed=False)
        task3 = Task(user_id=test_user.id, title="Medium priority", priority="medium", completed=False)

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Sort by priority (high to low)
        results = await TaskService.get_user_tasks(
            user_id=test_user.id,
            session=test_session,
            sort_by="priority",
            sort_order="asc"
        )

        assert len(results) == 3
        assert results[0].priority == "high"
        assert results[1].priority == "medium"
        assert results[2].priority == "low"


class TestTaskServiceDataIsolation:
    """Test data isolation between users"""

    @pytest.mark.asyncio
    async def test_user_only_sees_own_tasks(
        self, test_session: AsyncSession, test_user: User, test_user_2: User
    ):
        """Test that users only see their own tasks"""
        # Create tasks for both users
        task_user1 = Task(user_id=test_user.id, title="User 1 Task", priority="medium", completed=False)
        task_user2 = Task(user_id=test_user_2.id, title="User 2 Task", priority="high", completed=False)

        test_session.add_all([task_user1, task_user2])
        await test_session.commit()

        # Get tasks for user 1
        user1_tasks = await TaskService.get_user_tasks(
            user_id=test_user.id,
            session=test_session
        )

        # Should only see their own task
        assert len(user1_tasks) == 1
        assert user1_tasks[0].title == "User 1 Task"

    @pytest.mark.asyncio
    async def test_user_cannot_update_other_user_task(
        self, test_session: AsyncSession, test_user: User, test_user_2: User
    ):
        """Test that users cannot update other users' tasks"""
        # Create task for user 1
        task = Task(user_id=test_user.id, title="User 1 Task", priority="medium", completed=False)
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Try to update as user 2
        update_data = TaskUpdate(title="Hacked Title")
        result = await TaskService.update_task(
            task_id=task.id,
            user_id=test_user_2.id,
            task_data=update_data,
            session=test_session
        )

        # Should return None (not found)
        assert result is None
