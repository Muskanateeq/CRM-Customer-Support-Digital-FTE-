"""
Settings Service

Business logic for user settings and profile management.
"""

from typing import Optional, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from ..models.user import User
from ..models.user_settings import UserSettings, UserSettingsUpdate, UserProfileUpdate
from ..models.task import Task
from ..models.tag import Tag


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SettingsService:
    """Service for managing user settings and profile"""

    @staticmethod
    async def get_or_create_settings(user_id: str, session: AsyncSession) -> UserSettings:
        """
        Get user settings or create default settings if they don't exist.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            UserSettings object
        """
        statement = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(statement)
        settings = result.scalar_one_or_none()

        if not settings:
            # Create default settings
            settings = UserSettings(user_id=user_id)
            session.add(settings)
            await session.commit()
            await session.refresh(settings)

        return settings

    @staticmethod
    async def update_settings(
        user_id: str,
        settings_update: UserSettingsUpdate,
        session: AsyncSession
    ) -> UserSettings:
        """
        Update user settings.

        Args:
            user_id: User ID
            settings_update: Settings update data
            session: Database session

        Returns:
            Updated UserSettings object
        """
        settings = await SettingsService.get_or_create_settings(user_id, session)

        # Update only provided fields
        update_data = settings_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)

        session.add(settings)
        await session.commit()
        await session.refresh(settings)

        return settings

    @staticmethod
    async def update_profile(
        user_id: str,
        profile_update: UserProfileUpdate,
        session: AsyncSession
    ) -> User:
        """
        Update user profile.

        Args:
            user_id: User ID
            profile_update: Profile update data
            session: Database session

        Returns:
            Updated User object
        """
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Update only provided fields
        update_data = profile_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def change_password(
        user_id: str,
        current_password: str,
        new_password: str,
        session: AsyncSession
    ) -> bool:
        """
        Change user password.

        Note: Better Auth manages passwords. This endpoint is deprecated.
        Password changes should be handled through Better Auth on the frontend.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            session: Database session

        Returns:
            True if password changed successfully

        Raises:
            ValueError: Password management is handled by Better Auth
        """
        raise ValueError(
            "Password management is handled by Better Auth. "
            "Please use the Better Auth password reset flow on the frontend."
        )

    @staticmethod
    async def export_user_data(user_id: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Export all user data.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            Dictionary containing all user data
        """
        # Get user profile
        user_statement = select(User).where(User.id == user_id)
        user_result = await session.execute(user_statement)
        user = user_result.scalar_one_or_none()

        # Get user settings
        settings = await SettingsService.get_or_create_settings(user_id, session)

        # Get all tasks
        tasks_statement = select(Task).where(Task.user_id == user_id)
        tasks_result = await session.execute(tasks_statement)
        tasks = tasks_result.scalars().all()

        # Get all tags
        tags_statement = select(Tag).where(Tag.user_id == user_id)
        tags_result = await session.execute(tags_statement)
        tags = tags_result.scalars().all()

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "emailVerified": user.emailVerified,
                "image": user.image,
                "createdAt": user.createdAt.isoformat(),
                "updatedAt": user.updatedAt.isoformat()
            },
            "settings": {
                "email_notifications": settings.email_notifications,
                "browser_notifications": settings.browser_notifications,
                "task_reminders": settings.task_reminders,
                "dnd_enabled": settings.dnd_enabled,
                "dnd_start": settings.dnd_start.isoformat() if settings.dnd_start else None,
                "dnd_end": settings.dnd_end.isoformat() if settings.dnd_end else None,
                "theme": settings.theme,
                "font_size": settings.font_size,
                "view_mode": settings.view_mode,
                "default_priority": settings.default_priority,
                "default_sort": settings.default_sort,
                "show_completed": settings.show_completed,
                "language": settings.language
            },
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "due_time": task.due_time.isoformat() if task.due_time else None,
                    "tags": task.tags,
                    "recurrence_pattern": task.recurrence_pattern,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ],
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "created_at": tag.created_at.isoformat()
                }
                for tag in tags
            ],
            "export_date": None  # Will be set by API endpoint
        }

    @staticmethod
    async def delete_account(user_id: str, session: AsyncSession) -> bool:
        """
        Delete user account and all associated data.

        Args:
            user_id: User ID
            session: Database session

        Returns:
            True if account deleted successfully
        """
        # Delete all tasks
        tasks_statement = select(Task).where(Task.user_id == user_id)
        tasks_result = await session.execute(tasks_statement)
        tasks = tasks_result.scalars().all()
        for task in tasks:
            await session.delete(task)

        # Delete all tags
        tags_statement = select(Tag).where(Tag.user_id == user_id)
        tags_result = await session.execute(tags_statement)
        tags = tags_result.scalars().all()
        for tag in tags:
            await session.delete(tag)

        # Delete settings
        settings_statement = select(UserSettings).where(UserSettings.user_id == user_id)
        settings_result = await session.execute(settings_statement)
        settings = settings_result.scalar_one_or_none()
        if settings:
            await session.delete(settings)

        # Delete user
        user_statement = select(User).where(User.id == user_id)
        user_result = await session.execute(user_statement)
        user = user_result.scalar_one_or_none()
        if user:
            await session.delete(user)

        await session.commit()
        return True
