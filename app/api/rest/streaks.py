"""
Streaks REST endpoints.
"""
from datetime import date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.streak import StreakResponse, StreakHistoryResponse, StreakHistoryListResponse
from app.services.streak_service import StreakService

router = APIRouter(prefix="/streaks", tags=["streaks"])


@router.get("", response_model=StreakResponse)
async def get_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current streak information for the authenticated user."""
    streak = await StreakService.get_current_streak(db, current_user.id)
    
    # Check if streak is active (completed a task today)
    today = date.today()
    is_active = streak.last_completion_date == today
    
    # Convert to response format
    return StreakResponse(
        id=streak.id,
        user_id=streak.user_id,
        current_streak=streak.current_streak,
        last_completion_date=streak.last_completion_date,
        is_active=is_active,
        created_at=streak.created_at,
        updated_at=streak.updated_at
    )


@router.get("/history", response_model=StreakHistoryListResponse)
async def get_streak_history(
    start_date: Optional[date] = Query(None, description="Start date for history (defaults to 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date for history (defaults to today)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of entries to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get streak history for the authenticated user."""
    # Set default date range if not provided
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    history = await StreakService.get_streak_history(
        db, current_user.id, start_date, end_date, limit
    )
    
    best_streak = await StreakService.get_best_streak(db, current_user.id)
    
    history_responses = [
        StreakHistoryResponse(
            id=entry.id,
            user_id=entry.user_id,
            date=entry.date,
            completed=entry.completed,
            streak_count=entry.streak_count,
            created_at=entry.created_at
        )
        for entry in history
    ]
    
    return StreakHistoryListResponse(
        history=history_responses,
        total=len(history_responses),
        best_streak=best_streak
    )

