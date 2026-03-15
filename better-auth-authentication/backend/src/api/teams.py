"""
Team API Endpoints

Handles team management operations:
- Create team
- Get user teams
- Get team details
- Update team
- Delete team
- Get team members
- Invite members
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user
from src.services.team_service import TeamService
from src.models.team import TeamCreate, TeamUpdate, TeamPublic

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamPublic, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new team.

    The current user becomes the team creator and admin.
    """
    team = await TeamService.create_team(
        user_id=current_user,
        team_data=team_data,
        session=session,
    )
    return team


@router.get("", response_model=List[TeamPublic])
async def get_user_teams(
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all teams where the current user is a member.
    """
    teams = await TeamService.get_user_teams(
        user_id=current_user,
        session=session,
    )
    return teams


@router.get("/{team_id}", response_model=TeamPublic)
async def get_team(
    team_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get team details by ID.

    Only accessible to team members.
    """
    team = await TeamService.get_team_by_id(
        team_id=team_id,
        user_id=current_user,
        session=session,
    )

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or you are not a member",
        )

    return team


@router.put("/{team_id}", response_model=TeamPublic)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update team details.

    Only accessible to team admins.
    """
    team = await TeamService.update_team(
        team_id=team_id,
        user_id=current_user,
        team_data=team_data,
        session=session,
    )

    if not team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this team",
        )

    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a team.

    Only accessible to team creator.
    """
    success = await TeamService.delete_team(
        team_id=team_id,
        user_id=current_user,
        session=session,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this team",
        )


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all members of a team.

    Only accessible to team members.
    """
    members = await TeamService.get_team_members(
        team_id=team_id,
        user_id=current_user,
        session=session,
    )

    if members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or you are not a member",
        )

    return members


@router.post("/{team_id}/invite")
async def invite_member(
    team_id: int,
    email: str,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Invite a member to the team.

    Only accessible to team admins.
    """
    invitation = await TeamService.invite_member(
        team_id=team_id,
        user_id=current_user,
        email=email,
        session=session,
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to invite members to this team",
        )

    return invitation
