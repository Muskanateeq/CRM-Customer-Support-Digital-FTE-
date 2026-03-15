"""
Settings API Routes

Endpoints for user settings and profile management.
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..api.deps import get_session, get_current_user
from ..models.user import User, UserPublic
from ..models.user_settings import (
    UserSettings,
    UserSettingsUpdate,
    UserProfileUpdate,
    ChangePasswordRequest
)
from ..services.settings_service import SettingsService


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=UserSettings)
async def get_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current user settings.

    Returns user settings or creates default settings if they don't exist.
    """
    try:
        print(f"[DEBUG] Getting settings for user: {current_user.id}")
        print(f"[DEBUG] User object: id={current_user.id}, email={current_user.email}")

        settings = await SettingsService.get_or_create_settings(
            current_user.id,
            session
        )

        print(f"[DEBUG] Settings retrieved successfully: {settings}")
        return settings
    except Exception as e:
        print(f"[ERROR] Settings API failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve settings: {str(e)}"
        )


@router.put("/", response_model=UserSettings)
async def update_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update user settings.

    Only provided fields will be updated.
    """
    try:
        settings = await SettingsService.update_settings(
            current_user.id,
            settings_update,
            session
        )
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.get("/profile", response_model=UserPublic)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.

    Returns public user information.
    """
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        emailVerified=current_user.emailVerified,
        image=current_user.image,
        createdAt=current_user.createdAt,
        updatedAt=current_user.updatedAt
    )


@router.put("/profile", response_model=UserPublic)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update user profile.

    Only provided fields will be updated.
    """
    try:
        user = await SettingsService.update_profile(
            current_user.id,
            profile_update,
            session
        )
        return UserPublic(
            id=user.id,
            email=user.email,
            name=user.name,
            emailVerified=user.emailVerified,
            image=user.image,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Change user password.

    Requires current password for verification.
    """
    try:
        await SettingsService.change_password(
            current_user.id,
            password_request.current_password,
            password_request.new_password,
            session
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.get("/export", response_model=Dict[str, Any])
async def export_data(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Export all user data.

    Returns a JSON object containing user profile, settings, tasks, and tags.
    """
    try:
        data = await SettingsService.export_user_data(current_user.id, session)
        data["export_date"] = datetime.utcnow().isoformat()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete user account and all associated data.

    This action is permanent and cannot be undone.
    All tasks, tags, and settings will be deleted.
    """
    try:
        await SettingsService.delete_account(current_user.id, session)
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
