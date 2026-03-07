"""
Focus and Pomodoro schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.focus import SessionType


class PomodoroSessionBase(BaseModel):
    """Base Pomodoro session schema."""
    session_type: SessionType
    planned_duration_minutes: int
    task_id: Optional[int] = None
    notes: Optional[str] = None


class PomodoroSessionCreate(PomodoroSessionBase):
    """Schema for Pomodoro session creation."""
    pass


class PomodoroSessionResponse(PomodoroSessionBase):
    """Schema for Pomodoro session response."""
    id: int
    user_id: int
    duration_minutes: float  # Decimal minutes (includes seconds precision)
    started_at: datetime
    ended_at: Optional[datetime]
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class FocusStatsResponse(BaseModel):
    """Focus statistics response."""
    total_minutes_today: float  # Decimal minutes (includes seconds precision)
    total_minutes_this_week: float  # Decimal minutes (includes seconds precision)
    sessions_today: int
    sessions_this_week: int
    average_session_duration: float

