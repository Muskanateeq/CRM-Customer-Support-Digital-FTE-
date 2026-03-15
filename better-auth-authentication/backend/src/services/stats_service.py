"""
Statistics Service

Provides task statistics and analytics calculations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task


class StatsService:
    """Service for calculating task statistics"""

    @staticmethod
    async def get_task_summary(user_id: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Get comprehensive task statistics summary for a user.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            Dictionary with task statistics including:
            - total_tasks: Total number of tasks
            - completed_tasks: Number of completed tasks
            - in_progress_tasks: Number of in-progress tasks
            - overdue_tasks: Number of overdue tasks
            - completion_rate: Percentage of completed tasks
            - priority_distribution: Count by priority
            - tasks_by_status: Count by completion status
            - trend: Comparison with previous period
        """
        # Get current date
        now = datetime.utcnow()
        today = now.date()
        week_ago = today - timedelta(days=7)

        # Total tasks
        total_result = await session.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        total_tasks = total_result.scalar() or 0

        # Completed tasks
        completed_result = await session.execute(
            select(func.count(Task.id)).where(
                and_(Task.user_id == user_id, Task.completed == True)
            )
        )
        completed_tasks = completed_result.scalar() or 0

        # In-progress tasks
        in_progress_tasks = total_tasks - completed_tasks

        # Overdue tasks (not completed and due date in the past)
        overdue_result = await session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == False,
                    Task.due_date < today
                )
            )
        )
        overdue_tasks = overdue_result.scalar() or 0

        # Completion rate
        completion_rate = (
            round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0
        )

        # Priority distribution
        priority_result = await session.execute(
            select(Task.priority, func.count(Task.id))
            .where(Task.user_id == user_id)
            .group_by(Task.priority)
        )
        priority_distribution = {
            priority: count for priority, count in priority_result.all()
        }

        # Tasks created this week
        tasks_this_week_result = await session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= week_ago
                )
            )
        )
        tasks_this_week = tasks_this_week_result.scalar() or 0

        # Tasks completed this week
        completed_this_week_result = await session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True,
                    Task.updated_at >= week_ago
                )
            )
        )
        completed_this_week = completed_this_week_result.scalar() or 0

        # Calculate trend (simple comparison with previous week)
        # For now, we'll use tasks created this week as a simple trend indicator
        trend_direction = "up" if tasks_this_week > 0 else "neutral"
        trend_percentage = 0  # Simplified for now

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": completion_rate,
            "priority_distribution": priority_distribution,
            "tasks_by_status": {
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "overdue": overdue_tasks,
            },
            "weekly_stats": {
                "tasks_created": tasks_this_week,
                "tasks_completed": completed_this_week,
            },
            "trend": {
                "direction": trend_direction,
                "percentage": trend_percentage,
            },
        }
