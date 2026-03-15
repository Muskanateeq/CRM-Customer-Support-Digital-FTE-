"""
Comment Service

Business logic for task comments and mentions.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.comment import Comment, CommentCreate, CommentUpdate, CommentPublic
from src.models.task import Task


class CommentService:
    """Service for managing task comments."""

    @staticmethod
    async def create_comment(
        task_id: int,
        user_id: str,
        comment_data: CommentCreate,
        session: AsyncSession,
    ) -> Optional[CommentPublic]:
        """
        Create a new comment on a task.

        Args:
            task_id: Task ID to comment on
            user_id: User ID creating the comment
            comment_data: Comment data
            session: Database session

        Returns:
            Created comment or None if task not found
        """
        # Verify task exists
        task_result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return None

        # Create comment
        comment = Comment(
            task_id=task_id,
            author_id=user_id,
            content=comment_data.content,
            mentions=comment_data.mentions,
        )

        session.add(comment)
        await session.commit()
        await session.refresh(comment)

        return CommentPublic(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            content=comment.content,
            mentions=comment.mentions,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    @staticmethod
    async def get_task_comments(
        task_id: int,
        session: AsyncSession,
    ) -> List[CommentPublic]:
        """
        Get all comments for a task.

        Args:
            task_id: Task ID
            session: Database session

        Returns:
            List of comments ordered by creation time
        """
        result = await session.execute(
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
        )
        comments = result.scalars().all()

        return [
            CommentPublic(
                id=comment.id,
                task_id=comment.task_id,
                author_id=comment.author_id,
                content=comment.content,
                mentions=comment.mentions,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment in comments
        ]

    @staticmethod
    async def update_comment(
        comment_id: int,
        user_id: str,
        comment_data: CommentUpdate,
        session: AsyncSession,
    ) -> Optional[CommentPublic]:
        """
        Update a comment.

        Only the comment author can update it.

        Args:
            comment_id: Comment ID
            user_id: User ID requesting update
            comment_data: Updated comment data
            session: Database session

        Returns:
            Updated comment or None if not found/unauthorized
        """
        result = await session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment or comment.author_id != user_id:
            return None

        # Update content
        comment.content = comment_data.content

        await session.commit()
        await session.refresh(comment)

        return CommentPublic(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            content=comment.content,
            mentions=comment.mentions,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    @staticmethod
    async def delete_comment(
        comment_id: int,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """
        Delete a comment.

        Only the comment author can delete it.

        Args:
            comment_id: Comment ID
            user_id: User ID requesting deletion
            session: Database session

        Returns:
            True if deleted, False if not found/unauthorized
        """
        result = await session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment or comment.author_id != user_id:
            return False

        await session.delete(comment)
        await session.commit()

        return True
