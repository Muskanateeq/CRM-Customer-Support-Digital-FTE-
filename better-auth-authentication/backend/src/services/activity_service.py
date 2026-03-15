"""
Activity Service Layer

Business logic for activity tracking and history management.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from sqlalchemy.exc import SQLAlchemyError

from src.models.activity import Activity, ActivityCreate, ActivityPublic


class ActivityService:
    """Service class for activity operations"""

    @staticmethod
    async def create_activity(
        user_id: str,
        activity_data: ActivityCreate,
        session: AsyncSession
    ) -> Activity:
        """
        Create a new activity log entry.

        Args:
            user_id: User ID from JWT token
            activity_data: Activity data
            session: Database session

        Returns:
            Created activity
        """
        activity = Activity(
            user_id=user_id,
            type=activity_data.type,
            title=activity_data.title,
            description=activity_data.description,
            meta=activity_data.meta
        )

        session.add(activity)
        await session.commit()
        await session.refresh(activity)

        return activity

    @staticmethod
    async def log_activity(
        user_id: str,
        activity_type: str,
        title: str,
        description: str,
        meta: Optional[dict],
        session: AsyncSession
    ) -> Activity:
        """
        Quick helper to log an activity.

        Args:
            user_id: User ID
            activity_type: Activity type (created, updated, deleted, etc.)
            title: Activity title
            description: Activity description
            meta: Additional metadata
            session: Database session

        Returns:
            Created activity
        """
        activity_data = ActivityCreate(
            type=activity_type,
            title=title,
            description=description,
            meta=meta
        )
        return await ActivityService.create_activity(user_id, activity_data, session)

    @staticmethod
    async def get_user_activities(
        user_id: str,
        session: AsyncSession,
        activity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Activity]:
        """
        Get user's activity history.

        Args:
            user_id: User ID from JWT token
            session: Database session
            activity_type: Optional filter by activity type
            limit: Maximum number of activities to return
            offset: Number of activities to skip

        Returns:
            List of activities
        """
        query = select(Activity).where(Activity.user_id == user_id)

        if activity_type:
            query = query.where(Activity.type == activity_type)

        query = query.order_by(desc(Activity.created_at)).limit(limit).offset(offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete_activity(
        activity_id: int,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Delete a specific activity.

        Args:
            activity_id: Activity ID to delete
            user_id: User ID from JWT token (for authorization)
            session: Database session

        Returns:
            True if deleted, False if not found
        """
        query = select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == user_id
        )
        result = await session.execute(query)
        activity = result.scalar_one_or_none()

        if not activity:
            return False

        await session.delete(activity)
        await session.commit()
        return True

    @staticmethod
    async def clear_user_activities(
        user_id: str,
        session: AsyncSession
    ) -> int:
        """
        Clear all activities for a user.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            Number of activities deleted
        """
        query = delete(Activity).where(Activity.user_id == user_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount
