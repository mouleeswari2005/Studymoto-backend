"""
Streak schemas for API responses.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


class StreakResponse(BaseModel):
    """Schema for streak response."""
    id: int
    user_id: int
    current_streak: int
    last_completion_date: Optional[date]
    is_active: bool  # True if completed a task today
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StreakHistoryResponse(BaseModel):
    """Schema for streak history entry."""
    id: int
    user_id: int
    date: date
    completed: bool
    streak_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StreakHistoryListResponse(BaseModel):
    """Schema for list of streak history entries."""
    history: List[StreakHistoryResponse]
    total: int
    best_streak: int

