"""
Task Assignment API Endpoints

Handles task assignment operations:
- Assign task to user
- Get task assignments
- Get user assignments
- Unassign task
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user
from src.services.task_assignment_service import TaskAssignmentService
from src.models.task_assignment import TaskAssignmentCreate, TaskAssignmentPublic

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/tasks/{task_id}/assign", response_model=TaskAssignmentPublic, status_code=status.HTTP_201_CREATED)
async def assign_task(
    task_id: int,
    assignment_data: TaskAssignmentCreate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Assign a task to a user.

    The current user becomes the assigner.
    """
    assignment = await TaskAssignmentService.assign_task(
        task_id=task_id,
        assignee_id=assignment_data.assignee_id,
        assigner_id=current_user,
        session=session,
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return assignment


@router.get("/tasks/{task_id}/assignments", response_model=List[TaskAssignmentPublic])
async def get_task_assignments(
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all assignments for a task.

    Returns assignments ordered by assignment time (newest first).
    """
    assignments = await TaskAssignmentService.get_task_assignments(
        task_id=task_id,
        session=session,
    )

    return assignments


@router.get("/users/me/assignments", response_model=List[TaskAssignmentPublic])
async def get_my_assignments(
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all task assignments for the current user.

    Returns assignments ordered by assignment time (newest first).
    """
    assignments = await TaskAssignmentService.get_user_assignments(
        user_id=current_user,
        session=session,
    )

    return assignments


@router.delete("/tasks/{task_id}/unassign/{assignee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_task(
    task_id: int,
    assignee_id: str,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Unassign a task from a user.

    Only the task owner or the assignee can unassign.
    """
    success = await TaskAssignmentService.unassign_task(
        task_id=task_id,
        assignee_id=assignee_id,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
