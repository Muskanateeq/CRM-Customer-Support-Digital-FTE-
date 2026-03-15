"""
Notification API Endpoints

Handles notification operations:
- Get user notifications
- Mark notification as read
- Mark all notifications as read
- Delete notification
- Get unread count
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user_id
from src.services.notification_service import NotificationService
from src.models.notification import NotificationPublic

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationPublic])
async def get_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get notifications for the current user.

    Returns notifications ordered by creation time (newest first).
    """
    notifications = await NotificationService.get_user_notifications(
        user_id=user_id,
        session=session,
        unread_only=unread_only,
        limit=limit,
    )

    return notifications


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get count of unread notifications for the current user.
    """
    count = await NotificationService.get_unread_count(
        user_id=user_id,
        session=session,
    )

    return {"count": count}


@router.put("/{notification_id}/read", response_model=NotificationPublic)
async def mark_notification_as_read(
    notification_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Mark a notification as read.

    Only the notification owner can mark it as read.
    """
    notification = await NotificationService.mark_as_read(
        notification_id=notification_id,
        user_id=user_id,
        session=session,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.put("/read-all", response_model=dict)
async def mark_all_as_read(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Mark all notifications as read for the current user.
    """
    count = await NotificationService.mark_all_as_read(
        user_id=user_id,
        session=session,
    )

    return {"marked_read": count}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a notification.

    Only the notification owner can delete it.
    """
    success = await NotificationService.delete_notification(
        notification_id=notification_id,
        user_id=user_id,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
