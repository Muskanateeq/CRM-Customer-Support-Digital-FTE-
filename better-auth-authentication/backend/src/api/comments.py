"""
Comment API Endpoints

Handles comment operations:
- Create comment on task
- Get task comments
- Update comment
- Delete comment
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user
from src.services.comment_service import CommentService
from src.models.comment import CommentCreate, CommentUpdate, CommentPublic

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/tasks/{task_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new comment on a task.

    Supports @mentions for notifying team members.
    """
    comment = await CommentService.create_comment(
        task_id=task_id,
        user_id=current_user,
        comment_data=comment_data,
        session=session,
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return comment


@router.get("/tasks/{task_id}/comments", response_model=List[CommentPublic])
async def get_task_comments(
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all comments for a task.

    Returns comments ordered by creation time (oldest first).
    """
    comments = await CommentService.get_task_comments(
        task_id=task_id,
        session=session,
    )

    return comments


@router.put("/{comment_id}", response_model=CommentPublic)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a comment.

    Only the comment author can update it.
    """
    comment = await CommentService.update_comment(
        comment_id=comment_id,
        user_id=current_user,
        comment_data=comment_data,
        session=session,
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you are not the author",
        )

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a comment.

    Only the comment author can delete it.
    """
    success = await CommentService.delete_comment(
        comment_id=comment_id,
        user_id=current_user,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you are not the author",
        )
