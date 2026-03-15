"""
Project API Endpoints

Handles project management operations:
- Create project
- Get user projects
- Get project details
- Update project
- Delete project
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user
from src.services.project_service import ProjectService
from src.models.project import ProjectCreate, ProjectUpdate, ProjectPublic

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new project.

    The current user becomes the project owner.
    """
    project = await ProjectService.create_project(
        user_id=current_user,
        project_data=project_data,
        session=session,
    )

    return project


@router.get("", response_model=List[ProjectPublic])
async def get_user_projects(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, archived"),
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all projects for the current user.

    Optionally filter by status.
    """
    projects = await ProjectService.get_user_projects(
        user_id=current_user,
        session=session,
        status=status,
    )

    return projects


@router.get("/{project_id}", response_model=ProjectPublic)
async def get_project(
    project_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get project details by ID.

    Only accessible to the project owner.
    """
    project = await ProjectService.get_project_by_id(
        project_id=project_id,
        user_id=current_user,
        session=session,
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.put("/{project_id}", response_model=ProjectPublic)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update project details.

    Only accessible to the project owner.
    """
    project = await ProjectService.update_project(
        project_id=project_id,
        user_id=current_user,
        project_data=project_data,
        session=session,
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a project.

    Only accessible to the project owner.
    """
    success = await ProjectService.delete_project(
        project_id=project_id,
        user_id=current_user,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
