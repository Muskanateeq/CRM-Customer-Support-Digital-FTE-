"""
Background Scheduler for TaskNest

Runs periodic tasks like checking due dates and creating notifications.
"""

import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.models.task import Task
from src.models.notification import Notification


class TaskScheduler:
    """Background scheduler for task-related jobs"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def check_due_tasks(self):
        """
        Check for tasks that are due soon or overdue and create notifications.

        Runs every 1 hour.
        """
        try:
            async with AsyncSessionLocal() as session:
                now = datetime.utcnow()
                tomorrow = now + timedelta(days=1)

                print(f"[Scheduler] Checking due tasks at {now}")

                # Get tasks due in next 24 hours (not completed, not deleted)
                query = select(Task).where(
                    and_(
                        Task.deleted_at.is_(None),
                        Task.completed == False,
                        Task.due_date.isnot(None),
                        Task.due_date <= tomorrow,
                        Task.due_date > now
                    )
                )
                result = await session.execute(query)
                due_soon_tasks = result.scalars().all()

                # Create notifications for tasks due soon
                for task in due_soon_tasks:
                    # Check if notification already exists in last 24 hours
                    existing = await session.execute(
                        select(Notification).where(
                            and_(
                                Notification.user_id == task.user_id,
                                Notification.type == "task_due_soon",
                                Notification.related_item_id == task.id,
                                Notification.created_at >= now - timedelta(hours=24)
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue  # Already notified

                    # Create notification
                    notification = Notification(
                        user_id=task.user_id,
                        type="task_due_soon",
                        content=f"Task '{task.title}' is due on {task.due_date.strftime('%Y-%m-%d')}",
                        related_item_type="task",
                        related_item_id=task.id,
                        read=False
                    )
                    session.add(notification)
                    print(f"[Scheduler] Created 'due soon' notification for task: {task.title}")

                # Get overdue tasks
                overdue_query = select(Task).where(
                    and_(
                        Task.deleted_at.is_(None),
                        Task.completed == False,
                        Task.due_date.isnot(None),
                        Task.due_date < now
                    )
                )
                overdue_result = await session.execute(overdue_query)
                overdue_tasks = overdue_result.scalars().all()

                # Create notifications for overdue tasks
                for task in overdue_tasks:
                    # Check if notification already exists today
                    existing = await session.execute(
                        select(Notification).where(
                            and_(
                                Notification.user_id == task.user_id,
                                Notification.type == "task_overdue",
                                Notification.related_item_id == task.id,
                                Notification.created_at >= now - timedelta(hours=24)
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue  # Already notified today

                    # Create notification
                    notification = Notification(
                        user_id=task.user_id,
                        type="task_overdue",
                        content=f"Task '{task.title}' was due on {task.due_date.strftime('%Y-%m-%d')}",
                        related_item_type="task",
                        related_item_id=task.id,
                        read=False
                    )
                    session.add(notification)
                    print(f"[Scheduler] Created 'overdue' notification for task: {task.title}")

                await session.commit()
                print(f"[Scheduler] Completed: {len(due_soon_tasks)} due soon, {len(overdue_tasks)} overdue")

        except Exception as e:
            print(f"[Scheduler] Error checking due tasks: {e}")

    def start(self):
        """Start the scheduler"""
        # Check due tasks every 1 hour
        self.scheduler.add_job(
            self.check_due_tasks,
            trigger=IntervalTrigger(hours=1),
            id="check_due_tasks",
            name="Check for due and overdue tasks",
            replace_existing=True
        )

        # Run immediately on startup
        self.scheduler.add_job(
            self.check_due_tasks,
            id="check_due_tasks_startup",
            name="Initial check for due tasks"
        )

        self.scheduler.start()
        print("[Scheduler] Started background scheduler - checking tasks every 1 hour")

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        print("[Scheduler] Stopped background scheduler")


# Global scheduler instance
scheduler = TaskScheduler()
