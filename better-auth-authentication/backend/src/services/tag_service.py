"""
Tag Service Layer

Business logic for tag operations including:
- CRUD operations
- Ownership validation
- Duplicate name prevention
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError

from src.models.tag import Tag, TagCreate, TagUpdate, TagPublic


class TagService:
    """Service class for tag operations"""

    @staticmethod
    async def create_tag(
        user_id: str,
        tag_data: TagCreate,
        session: AsyncSession
    ) -> Optional[TagPublic]:
        """
        Create a new tag for the user.

        Args:
            user_id: User ID from JWT token
            tag_data: Tag creation data
            session: Database session

        Returns:
            Created tag, or None if tag name already exists for user

        Raises:
            IntegrityError: If tag name already exists for user
        """
        # Check if tag name already exists for this user
        result = await session.execute(
            select(Tag).where(
                and_(Tag.user_id == user_id, Tag.name == tag_data.name)
            )
        )
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            return None

        # Create tag
        tag = Tag(
            user_id=user_id,
            name=tag_data.name,
        )

        session.add(tag)

        try:
            await session.commit()
            await session.refresh(tag)
        except IntegrityError:
            await session.rollback()
            return None

        return TagPublic(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
        )

    @staticmethod
    async def get_user_tags(
        user_id: str,
        session: AsyncSession
    ) -> List[TagPublic]:
        """
        Get all tags for a user.

        Args:
            user_id: User ID from JWT token
            session: Database session

        Returns:
            List of tags ordered by name
        """
        result = await session.execute(
            select(Tag)
            .where(Tag.user_id == user_id)
            .order_by(Tag.name.asc())
        )
        tags = result.scalars().all()

        return [
            TagPublic(
                id=tag.id,
                name=tag.name,
                created_at=tag.created_at,
            )
            for tag in tags
        ]

    @staticmethod
    async def get_tag_by_id(
        tag_id: int,
        user_id: str,
        session: AsyncSession
    ) -> Optional[TagPublic]:
        """
        Get a single tag by ID.

        Args:
            tag_id: Tag ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            Tag if found and owned by user, None otherwise
        """
        result = await session.execute(
            select(Tag).where(
                and_(Tag.id == tag_id, Tag.user_id == user_id)
            )
        )
        tag = result.scalar_one_or_none()

        if not tag:
            return None

        return TagPublic(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
        )

    @staticmethod
    async def update_tag(
        tag_id: int,
        user_id: str,
        tag_data: TagUpdate,
        session: AsyncSession
    ) -> Optional[TagPublic]:
        """
        Update a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID from JWT token (for ownership validation)
            tag_data: Tag update data
            session: AsyncSession

        Returns:
            Updated tag if found and owned by user, None otherwise
        """
        # Get tag
        result = await session.execute(
            select(Tag).where(
                and_(Tag.id == tag_id, Tag.user_id == user_id)
            )
        )
        tag = result.scalar_one_or_none()

        if not tag:
            return None

        # Check if new name already exists for this user (excluding current tag)
        name_check = await session.execute(
            select(Tag).where(
                and_(
                    Tag.user_id == user_id,
                    Tag.name == tag_data.name,
                    Tag.id != tag_id
                )
            )
        )
        existing_tag = name_check.scalar_one_or_none()

        if existing_tag:
            return None

        # Update name
        tag.name = tag_data.name

        try:
            await session.commit()
            await session.refresh(tag)
        except IntegrityError:
            await session.rollback()
            return None

        return TagPublic(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
        )

    @staticmethod
    async def delete_tag(
        tag_id: int,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Delete a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID from JWT token (for ownership validation)
            session: Database session

        Returns:
            True if tag was deleted, False if not found or not owned by user
        """
        # Get tag
        result = await session.execute(
            select(Tag).where(
                and_(Tag.id == tag_id, Tag.user_id == user_id)
            )
        )
        tag = result.scalar_one_or_none()

        if not tag:
            return False

        # Delete tag (cascade will delete task_tags)
        await session.delete(tag)
        await session.commit()

        return True
