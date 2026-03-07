"""
Focus and productivity tools models.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class SessionType(str, Enum):
    """Pomodoro session type enumeration."""
    STUDY = "study"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class PomodoroSession(Base):
    """Pomodoro timer session model."""
    __tablename__ = "pomodoro_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    session_type = Column(String, nullable=False)  # SessionType enum
    duration_minutes = Column(Float, nullable=False)  # Actual duration in decimal minutes (includes seconds)
    planned_duration_minutes = Column(Integer, nullable=False)  # Planned duration (usually 25 for study)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="pomodoro_sessions")

