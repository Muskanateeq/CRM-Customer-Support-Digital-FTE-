"""
Tag API Endpoints

RESTful API endpoints for tag management with:
- CRUD operations
- User ownership enforcement
- Duplicate name prevention
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.api.deps import get_current_user_id
from src.models.tag import TagCreate, TagUpdate, TagPublic
from src.services.tag_service import TagService

# Create router
router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post(
    "",
    response_model=TagPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create tag",
    description="Create a new tag for the authenticated user"
)
async def create_tag(
    tag_data: TagCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TagPublic:
    """
    Create a new tag.

    - **name**: Tag name (required, 1-50 characters, must be unique per user)

    Returns created tag.

    Raises:
        409: Tag name already exists for this user
    """
    tag = await TagService.create_tag(user_id, tag_data, session)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag_data.name}' already exists"
        )

    return tag


@router.get(
    "",
    response_model=List[TagPublic],
    summary="List tags",
    description="Get all tags for the authenticated user"
)
async def list_tags(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> List[TagPublic]:
    """
    Get all tags for the authenticated user.

    Returns list of tags ordered by name.
    """
    return await TagService.get_user_tags(user_id, session)


@router.get(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Get tag",
    description="Get a single tag by ID"
)
async def get_tag(
    tag_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TagPublic:
    """
    Get a single tag by ID.

    Returns tag if found and owned by user.

    Raises:
        404: Tag not found or not owned by user
    """
    tag = await TagService.get_tag_by_id(tag_id, user_id, session)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    return tag


@router.put(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Update tag",
    description="Update a tag by ID"
)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> TagPublic:
    """
    Update a tag.

    - **name**: New tag name (required, 1-50 characters, must be unique per user)

    Returns updated tag.

    Raises:
        404: Tag not found or not owned by user
        409: Tag name already exists for this user
    """
    tag = await TagService.update_tag(tag_id, user_id, tag_data, session)

    if not tag:
        # Check if tag exists
        existing_tag = await TagService.get_tag_by_id(tag_id, user_id, session)
        if not existing_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with ID {tag_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag with name '{tag_data.name}' already exists"
            )

    return tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tag",
    description="Delete a tag by ID"
)
async def delete_tag(
    tag_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a tag.

    Permanently removes the tag and its task associations.

    Raises:
        404: Tag not found or not owned by user
    """
    success = await TagService.delete_tag(tag_id, user_id, session)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    return None
