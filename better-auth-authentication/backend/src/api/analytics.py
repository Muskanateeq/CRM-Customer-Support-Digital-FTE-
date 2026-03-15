"""
Analytics API Routes

Endpoints for analytics and insights.
"""

from typing import Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ..api.deps import get_session, get_current_user
from ..models.user import User
from ..services.analytics_service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/completion-rate")
async def get_completion_rate(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get task completion rate over time.

    Returns daily completion statistics for the specified date range.
    Defaults to last 30 days if no dates provided.
    """
    try:
        # Default to last 30 days
        if not end_date:
            end_date = datetime.utcnow().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        data = await AnalyticsService.get_completion_rate_over_time(
            current_user.id,
            start_date,
            end_date,
            session
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve completion rate: {str(e)}"
        )


@router.get("/tasks-by-priority")
async def get_tasks_by_priority(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get task distribution by priority.

    Returns count of tasks for each priority level.
    """
    try:
        data = await AnalyticsService.get_tasks_by_priority(
            current_user.id,
            start_date,
            end_date,
            session
        )

        return {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve priority distribution: {str(e)}"
        )


@router.get("/tasks-by-tag")
async def get_tasks_by_tag(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get task distribution by tag.

    Returns top 10 most used tags with counts.
    """
    try:
        data = await AnalyticsService.get_tasks_by_tag(
            current_user.id,
            start_date,
            end_date,
            session
        )

        return {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tag distribution: {str(e)}"
        )


@router.get("/productivity-heatmap")
async def get_productivity_heatmap(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get productivity heatmap data.

    Returns task completion counts by day of week and hour of day.
    Defaults to last 30 days if no dates provided.
    """
    try:
        # Default to last 30 days
        if not end_date:
            end_date = datetime.utcnow().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        data = await AnalyticsService.get_productivity_heatmap(
            current_user.id,
            start_date,
            end_date,
            session
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve productivity heatmap: {str(e)}"
        )


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get AI-generated insights about user's productivity patterns.

    Returns personalized insights based on task completion history.
    """
    try:
        insights = await AnalyticsService.generate_insights(
            current_user.id,
            session
        )

        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/summary")
async def get_analytics_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get comprehensive analytics summary.

    Returns all analytics data in a single response for dashboard overview.
    """
    try:
        # Default to last 30 days
        if not end_date:
            end_date = datetime.utcnow().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Fetch all analytics data
        completion_rate = await AnalyticsService.get_completion_rate_over_time(
            current_user.id,
            start_date,
            end_date,
            session
        )

        priority_dist = await AnalyticsService.get_tasks_by_priority(
            current_user.id,
            start_date,
            end_date,
            session
        )

        tag_dist = await AnalyticsService.get_tasks_by_tag(
            current_user.id,
            start_date,
            end_date,
            session
        )

        heatmap = await AnalyticsService.get_productivity_heatmap(
            current_user.id,
            start_date,
            end_date,
            session
        )

        insights = await AnalyticsService.generate_insights(
            current_user.id,
            session
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "completion_rate": completion_rate,
            "tasks_by_priority": priority_dist,
            "tasks_by_tag": tag_dist,
            "productivity_heatmap": heatmap,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics summary: {str(e)}"
        )
