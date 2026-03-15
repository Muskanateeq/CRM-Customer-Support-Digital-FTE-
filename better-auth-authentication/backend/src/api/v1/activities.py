"""
Activity API Routes

Endpoints for activity tracking and history management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user_id
from src.models.activity import ActivityPublic, ActivityCreate
from src.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=List[ActivityPublic])
async def get_activities(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of activities"),
    offset: int = Query(0, ge=0, description="Number of activities to skip"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user's activity history.

    Returns list of activities ordered by most recent first.
    """
    activities = await ActivityService.get_user_activities(
        user_id=user_id,
        session=session,
        activity_type=activity_type,
        limit=limit,
        offset=offset
    )
    return activities


@router.post("", response_model=ActivityPublic, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new activity log entry.

    This is typically called automatically by the system,
    but can also be used manually if needed.
    """
    activity = await ActivityService.create_activity(
        user_id=user_id,
        activity_data=activity_data,
        session=session
    )
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a specific activity from history.
    """
    deleted = await ActivityService.delete_activity(
        activity_id=activity_id,
        user_id=user_id,
        session=session
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_activities(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Clear all activities for the current user.

    Returns the number of activities deleted.
    """
    count = await ActivityService.clear_user_activities(
        user_id=user_id,
        session=session
    )
    return {"deleted_count": count, "message": f"Cleared {count} activities"}
