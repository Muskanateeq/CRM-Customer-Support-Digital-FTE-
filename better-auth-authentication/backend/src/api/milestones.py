"""
Milestone API Endpoints

Handles milestone management operations:
- Create milestone
- Get project milestones
- Update milestone
- Delete milestone
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user
from src.services.milestone_service import MilestoneService
from src.models.milestone import MilestoneCreate, MilestoneUpdate, MilestonePublic

router = APIRouter(prefix="/milestones", tags=["milestones"])


@router.post("/projects/{project_id}/milestones", response_model=MilestonePublic, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: int,
    milestone_data: MilestoneCreate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new milestone for a project.

    Only the project owner can create milestones.
    """
    milestone = await MilestoneService.create_milestone(
        project_id=project_id,
        user_id=current_user,
        milestone_data=milestone_data,
        session=session,
    )

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return milestone


@router.get("/projects/{project_id}/milestones", response_model=List[MilestonePublic])
async def get_project_milestones(
    project_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all milestones for a project.

    Only the project owner can view milestones.
    """
    milestones = await MilestoneService.get_project_milestones(
        project_id=project_id,
        user_id=current_user,
        session=session,
    )

    if milestones is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return milestones


@router.put("/{milestone_id}", response_model=MilestonePublic)
async def update_milestone(
    milestone_id: int,
    milestone_data: MilestoneUpdate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a milestone.

    Only the project owner can update milestones.
    """
    milestone = await MilestoneService.update_milestone(
        milestone_id=milestone_id,
        user_id=current_user,
        milestone_data=milestone_data,
        session=session,
    )

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    return milestone


@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a milestone.

    Only the project owner can delete milestones.
    """
    success = await MilestoneService.delete_milestone(
        milestone_id=milestone_id,
        user_id=current_user,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )
