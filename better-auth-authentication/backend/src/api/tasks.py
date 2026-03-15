"""
Task API Endpoints

RESTful API endpoints for task management with:
- CRUD operations
- Search, filter, and sort
- Completion toggle
- User ownership enforcement
- Statistics and analytics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user_id
from src.models.task import TaskCreate, TaskUpdate, TaskPublic, TaskCompletionToggle
from src.services.task_service import TaskService
from src.services.stats_service import StatsService

# Create router
router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task for the authenticated user"
)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    """
    Create a new task.

    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **priority**: Task priority (high, medium, low)
    - **due_date**: Due date (optional)
    - **due_time**: Due time (optional)
    - **recurrence_pattern**: Recurrence pattern (optional, JSON)
    - **tag_ids**: List of tag IDs to associate (optional)

    Returns created task with tags.
    """
    return await TaskService.create_task(user_id, task_data, session)


@router.get(
    "",
    response_model=List[TaskPublic],
    summary="List tasks",
    description="Get all tasks for the authenticated user with optional filters"
)
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    search: Optional[str] = Query(None, description="Search keyword (matches title and description)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: all, pending, completed"),
    priority: Optional[str] = Query(None, description="Filter by priority: high, medium, low"),
    tag_ids: Optional[str] = Query(None, description="Filter by tag IDs (comma-separated)"),
    due_date_filter: Optional[str] = Query(None, description="Filter by due date: overdue, today, week, month, none"),
    sort_by: str = Query("created_at", description="Sort by: created_at, due_date, priority, title"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> List[TaskPublic]:
    """
    Get all tasks for the authenticated user.

    Supports:
    - **Search**: Keyword search in title and description
    - **Filters**: Status, priority, tags, due date
    - **Sorting**: By creation date, due date, priority, or title
    - **Pagination**: Limit and offset

    Returns list of tasks with tags.
    """
    # Parse tag_ids from comma-separated string
    tag_ids_list = None
    if tag_ids:
        try:
            tag_ids_list = [int(tid.strip()) for tid in tag_ids.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Use comma-separated integers."
            )

    return await TaskService.get_user_tasks(
        user_id=user_id,
        session=session,
        search=search,
        status=status_filter,
        priority=priority,
        tag_ids=tag_ids_list,
        due_date_filter=due_date_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",
    response_model=TaskPublic,
    summary="Get task",
    description="Get a single task by ID"
)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    """
    Get a single task by ID.

    Returns task with tags if found and owned by user.

    Raises:
        404: Task not found or not owned by user
    """
    task = await TaskService.get_task_by_id(task_id, user_id, session)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskPublic,
    summary="Update task",
    description="Update a task by ID"
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    """
    Update a task.

    All fields are optional - only provided fields will be updated.

    Returns updated task with tags.

    Raises:
        404: Task not found or not owned by user
    """
    task = await TaskService.update_task(task_id, user_id, task_data, session)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by ID"
)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a task.

    Permanently removes the task and its tag associations.

    Raises:
        404: Task not found or not owned by user
    """
    success = await TaskService.delete_task(task_id, user_id, session)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return None


@router.get(
    "/stats/summary",
    response_model=Dict[str, Any],
    summary="Get task statistics",
    description="Get comprehensive task statistics and analytics for the authenticated user"
)
async def get_task_statistics(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get task statistics summary.

    Returns:
        - total_tasks: Total number of tasks
        - completed_tasks: Number of completed tasks
        - in_progress_tasks: Number of in-progress tasks
        - overdue_tasks: Number of overdue tasks
        - completion_rate: Percentage of completed tasks
        - priority_distribution: Count by priority
        - tasks_by_status: Count by completion status
        - weekly_stats: Tasks created/completed this week
        - trend: Trend indicators
    """
    return await StatsService.get_task_summary(user_id, session)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskPublic,
    summary="Toggle task completion",
    description="Mark task as complete or incomplete"
)
async def toggle_task_completion(
    task_id: int,
    completion_data: TaskCompletionToggle,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    """
    Toggle task completion status.

    For recurring tasks, marking as complete will create the next occurrence.

    Returns updated task with tags.

    Raises:
        404: Task not found or not owned by user
    """
    task = await TaskService.toggle_completion(
        task_id, user_id, completion_data.completed, session
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return task


@router.get(
    "/stats/summary",
    summary="Get task statistics",
    description="Get summary statistics for user's tasks"
)
async def get_task_stats(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Get task statistics for the authenticated user.

    Returns:
        - Total tasks
        - Completed tasks
        - Pending tasks
        - Overdue tasks
        - Tasks by priority
    """
    # Get all tasks
    all_tasks = await TaskService.get_user_tasks(
        user_id=user_id,
        session=session,
        limit=10000,  # Get all tasks for stats
    )

    from datetime import date
    today = date.today()

    # Calculate statistics
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.completed)
    pending = total - completed
    overdue = sum(
        1 for t in all_tasks
        if not t.completed and t.due_date and t.due_date < today
    )

    # Count by priority
    high_priority = sum(1 for t in all_tasks if t.priority == "high")
    medium_priority = sum(1 for t in all_tasks if t.priority == "medium")
    low_priority = sum(1 for t in all_tasks if t.priority == "low")

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "by_priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        }
    }
