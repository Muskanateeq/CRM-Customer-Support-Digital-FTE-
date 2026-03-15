"""
Base Pydantic Schemas

Provides base schemas and common response models for the API.
All request/response schemas should inherit from these base classes.
"""

from typing import Optional, Generic, TypeVar, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Generic type for data responses
T = TypeVar('T')


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.

    All Pydantic schemas should inherit from this class.
    """
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode (formerly orm_mode)
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


class TimestampSchema(BaseSchema):
    """
    Schema with timestamp fields.

    Use this for models that track creation and update times.
    """
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SuccessResponse(BaseSchema, Generic[T]):
    """
    Generic success response wrapper.

    Example:
        return SuccessResponse(
            success=True,
            message="Task created successfully",
            data=task
        )
    """
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[T] = Field(None, description="Response data")


class ErrorResponse(BaseSchema):
    """
    Error response model.

    Example:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                success=False,
                error="Invalid input",
                error_type="validation_error"
            ).model_dump()
        )
    """
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type identifier")
    details: Optional[dict] = Field(None, description="Additional error details")


class PaginationParams(BaseSchema):
    """
    Pagination parameters for list endpoints.

    Example:
        @app.get("/api/v1/tasks")
        async def get_tasks(
            pagination: PaginationParams = Depends()
        ):
            ...
    """
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Paginated response wrapper.

    Example:
        return PaginatedResponse(
            items=tasks,
            total=total_count,
            skip=0,
            limit=100
        )
    """
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    has_more: bool = Field(..., description="Whether more items are available")

    @classmethod
    def create(cls, items: List[T], total: int, skip: int, limit: int):
        """
        Create a paginated response with calculated has_more field.

        Args:
            items: List of items for current page
            total: Total number of items
            skip: Number of items skipped
            limit: Maximum items per page

        Returns:
            PaginatedResponse instance
        """
        has_more = (skip + len(items)) < total
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )


class HealthCheckResponse(BaseSchema):
    """
    Health check response model.
    """
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current server time")
