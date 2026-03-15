"""
Analytics Service

Business logic for analytics calculations and insights generation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from sqlmodel import select, func, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from collections import defaultdict

from ..models.task import Task


class AnalyticsService:
    """Service for calculating analytics and generating insights"""

    @staticmethod
    async def get_completion_rate_over_time(
        user_id: str,
        start_date: date,
        end_date: date,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Calculate task completion rate over time.

        Args:
            user_id: User ID
            start_date: Start date for analysis
            end_date: End date for analysis
            session: Database session

        Returns:
            List of data points with date, completed, and created counts
        """
        # Get all tasks created or completed in the date range
        statement = select(Task).where(
            and_(
                Task.user_id == user_id,
                or_(
                    and_(
                        Task.created_at >= datetime.combine(start_date, datetime.min.time()),
                        Task.created_at <= datetime.combine(end_date, datetime.max.time())
                    ),
                    and_(
                        Task.updated_at >= datetime.combine(start_date, datetime.min.time()),
                        Task.updated_at <= datetime.combine(end_date, datetime.max.time()),
                        Task.completed == True
                    )
                )
            )
        )
        result = await session.exec(statement)
        tasks = result.all()

        # Group by date
        daily_data = defaultdict(lambda: {"created": 0, "completed": 0})

        for task in tasks:
            # Count created tasks
            created_date = task.created_at.date()
            if start_date <= created_date <= end_date:
                daily_data[created_date]["created"] += 1

            # Count completed tasks
            if task.completed:
                completed_date = task.updated_at.date()
                if start_date <= completed_date <= end_date:
                    daily_data[completed_date]["completed"] += 1

        # Convert to list and fill missing dates
        result_list = []
        current_date = start_date
        while current_date <= end_date:
            data = daily_data.get(current_date, {"created": 0, "completed": 0})
            result_list.append({
                "date": current_date.isoformat(),
                "created": data["created"],
                "completed": data["completed"],
                "completion_rate": (data["completed"] / data["created"] * 100) if data["created"] > 0 else 0
            })
            current_date += timedelta(days=1)

        return result_list

    @staticmethod
    async def get_tasks_by_priority(
        user_id: str,
        start_date: Optional[date],
        end_date: Optional[date],
        session: AsyncSession
    ) -> Dict[str, int]:
        """
        Get task distribution by priority.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            session: Database session

        Returns:
            Dictionary with priority counts
        """
        conditions = [Task.user_id == user_id]

        if start_date and end_date:
            conditions.append(
                Task.created_at >= datetime.combine(start_date, datetime.min.time())
            )
            conditions.append(
                Task.created_at <= datetime.combine(end_date, datetime.max.time())
            )

        statement = select(Task.priority, func.count(Task.id)).where(
            and_(*conditions)
        ).group_by(Task.priority)

        result = await session.exec(statement)
        rows = result.all()

        return {
            "high": next((count for priority, count in rows if priority == "high"), 0),
            "medium": next((count for priority, count in rows if priority == "medium"), 0),
            "low": next((count for priority, count in rows if priority == "low"), 0)
        }

    @staticmethod
    async def get_tasks_by_tag(
        user_id: str,
        start_date: Optional[date],
        end_date: Optional[date],
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get task distribution by tag.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            session: Database session

        Returns:
            List of tag distributions
        """
        conditions = [Task.user_id == user_id]

        if start_date and end_date:
            conditions.append(
                Task.created_at >= datetime.combine(start_date, datetime.min.time())
            )
            conditions.append(
                Task.created_at <= datetime.combine(end_date, datetime.max.time())
            )

        statement = select(Task).where(and_(*conditions))
        result = await session.exec(statement)
        tasks = result.all()

        # Count tags
        tag_counts = defaultdict(int)
        for task in tasks:
            if task.tags:
                for tag in task.tags:
                    tag_counts[tag] += 1

        # Convert to list and sort by count
        tag_list = [
            {"tag": tag, "count": count}
            for tag, count in tag_counts.items()
        ]
        tag_list.sort(key=lambda x: x["count"], reverse=True)

        return tag_list[:10]  # Return top 10 tags

    @staticmethod
    async def get_productivity_heatmap(
        user_id: str,
        start_date: date,
        end_date: date,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Generate productivity heatmap data (day of week vs hour of day).

        Args:
            user_id: User ID
            start_date: Start date for analysis
            end_date: End date for analysis
            session: Database session

        Returns:
            List of heatmap data points
        """
        # Get completed tasks in date range
        statement = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.completed == True,
                Task.updated_at >= datetime.combine(start_date, datetime.min.time()),
                Task.updated_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
        result = await session.exec(statement)
        tasks = result.all()

        # Count completions by day of week and hour
        heatmap_data = defaultdict(lambda: defaultdict(int))

        for task in tasks:
            day_of_week = task.updated_at.strftime("%A")
            hour = task.updated_at.hour
            heatmap_data[day_of_week][hour] += 1

        # Convert to list format
        result_list = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            for hour in range(24):
                result_list.append({
                    "day": day,
                    "hour": hour,
                    "count": heatmap_data[day][hour]
                })

        return result_list

    @staticmethod
    async def generate_insights(
        user_id: str,
        session: AsyncSession
    ) -> List[str]:
        """
        Generate AI-like insights based on user's task patterns.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            List of insight strings
        """
        insights = []

        # Get last 30 days of data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        # Get all tasks
        statement = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.created_at >= start_date
            )
        )
        result = await session.exec(statement)
        tasks = result.all()

        if not tasks:
            return ["Start completing tasks to see personalized insights!"]

        # Calculate completion rate
        completed_tasks = [t for t in tasks if t.completed]
        completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0

        if completion_rate >= 80:
            insights.append(f"Excellent work! You've completed {completion_rate:.0f}% of your tasks this month.")
        elif completion_rate >= 50:
            insights.append(f"You're making good progress with a {completion_rate:.0f}% completion rate.")
        else:
            insights.append(f"Your completion rate is {completion_rate:.0f}%. Consider breaking tasks into smaller steps.")

        # Analyze by day of week
        day_completions = defaultdict(int)
        for task in completed_tasks:
            day_completions[task.updated_at.strftime("%A")] += 1

        if day_completions:
            most_productive_day = max(day_completions.items(), key=lambda x: x[1])
            insights.append(f"You're most productive on {most_productive_day[0]}s, completing {most_productive_day[1]} tasks on average.")

        # Analyze average completion time
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                time_diff = (task.updated_at - task.created_at).total_seconds() / 86400  # days
                completion_times.append(time_diff)

        if completion_times:
            avg_time = sum(completion_times) / len(completion_times)
            insights.append(f"Your average task completion time is {avg_time:.1f} days.")

        # Analyze priority distribution
        high_priority = len([t for t in tasks if t.priority == "high"])
        if high_priority > len(tasks) * 0.5:
            insights.append("You have many high-priority tasks. Consider delegating or breaking them down.")

        return insights[:5]  # Return top 5 insights
