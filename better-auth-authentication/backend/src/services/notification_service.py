"""
Notification Service

Business logic for user notifications including:
- Creating notifications
- Fetching user notifications
- Marking notifications as read
- Deleting notifications
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from src.models.notification import (
    Notification,
    NotificationCreate,
    NotificationPublic,
)


class NotificationService:
    """Service for managing user notifications."""

    @staticmethod
    async def create_notification(
        user_id: str,
        notification_data: NotificationCreate,
        session: AsyncSession,
    ) -> NotificationPublic:
        """
        Create a new notification for a user.

        Args:
            user_id: User ID to notify
            notification_data: Notification data
            session: Database session

        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            type=notification_data.type,
            content=notification_data.content,
            related_item_type=notification_data.related_item_type,
            related_item_id=notification_data.related_item_id,
            read=False,
        )

        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        return NotificationPublic(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            content=notification.content,
            related_item_type=notification.related_item_type,
            related_item_id=notification.related_item_id,
            read=notification.read,
            created_at=notification.created_at,
        )

    @staticmethod
    async def get_user_notifications(
        user_id: str,
        session: AsyncSession,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[NotificationPublic]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            session: Database session

        Returns:
            List of notifications ordered by creation time (newest first)
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.read == False)

        query = query.order_by(Notification.created_at.desc()).limit(limit)

        result = await session.execute(query)
        notifications = result.scalars().all()

        return [
            NotificationPublic(
                id=notification.id,
                user_id=notification.user_id,
                type=notification.type,
                content=notification.content,
                related_item_type=notification.related_item_type,
                related_item_id=notification.related_item_id,
                read=notification.read,
                created_at=notification.created_at,
            )
            for notification in notifications
        ]

    @staticmethod
    async def mark_as_read(
        notification_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> Optional[NotificationPublic]:
        """
        Mark a notification as read.

        Args:
            notification_id: Notification ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            Updated notification or None if not found/unauthorized
        """
        result = await session.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                )
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return None

        notification.read = True
        await session.commit()
        await session.refresh(notification)

        return NotificationPublic(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            content=notification.content,
            related_item_type=notification.related_item_type,
            related_item_id=notification.related_item_id,
            read=notification.read,
            created_at=notification.created_at,
        )

    @staticmethod
    async def mark_all_as_read(
        user_id: str,
        session: AsyncSession,
    ) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            Number of notifications marked as read
        """
        result = await session.execute(
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read == False,
                )
            )
            .values(read=True)
        )
        await session.commit()

        return result.rowcount

    @staticmethod
    async def delete_notification(
        notification_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: Notification ID
            user_id: User ID (for authorization)
            session: Database session

        Returns:
            True if deleted, False if not found/unauthorized
        """
        result = await session.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                )
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        await session.delete(notification)
        await session.commit()

        return True

    @staticmethod
    async def get_unread_count(
        user_id: str,
        session: AsyncSession,
    ) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            Count of unread notifications
        """
        result = await session.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read == False,
                )
            )
        )
        notifications = result.scalars().all()

        return len(notifications)
