"""
Trash API Routes

Endpoints for managing soft-deleted tasks (trash/recycle bin).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user_id
from src.models.task import TaskPublic
from src.services.trash_service import TrashService

router = APIRouter(prefix="/trash", tags=["trash"])


@router.get("", response_model=List[TaskPublic])
async def get_trash(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all deleted tasks (trash/recycle bin).

    Returns list of soft-deleted tasks ordered by deletion time.
    """
    tasks = await TrashService.get_deleted_tasks(
        user_id=user_id,
        session=session,
        limit=limit,
        offset=offset
    )
    return tasks


@router.post("/{task_id}/restore", response_model=TaskPublic)
async def restore_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Restore a deleted task from trash.

    Clears the deleted_at timestamp and makes the task active again.
    """
    task = await TrashService.restore_task(
        task_id=task_id,
        user_id=user_id,
        session=session
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in trash"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Permanently delete a task from trash.

    This action cannot be undone.
    """
    deleted = await TrashService.permanent_delete_task(
        task_id=task_id,
        user_id=user_id,
        session=session
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in trash"
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def empty_trash(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Permanently delete all tasks in trash.

    This action cannot be undone.
    Returns the number of tasks permanently deleted.
    """
    count = await TrashService.empty_trash(
        user_id=user_id,
        session=session
    )
    return {"deleted_count": count, "message": f"Permanently deleted {count} tasks"}
