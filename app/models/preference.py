"""
User preferences and personalization models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserPreference(Base):
    """User preferences model."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Theme and appearance
    theme_color = Column(String, nullable=True)  # Primary color hex
    banner_image_url = Column(String, nullable=True)
    
    # Calendar preferences
    default_calendar_view = Column(String, default="week", nullable=False)  # day, week, month
    time_format = Column(String, default="12h", nullable=False)  # 12h or 24h
    timezone = Column(String, default="Asia/Kolkata", nullable=False)
    week_start_day = Column(Integer, default=0, nullable=False)  # 0=Monday, 6=Sunday
    
    # Custom filters/views (stored as JSON)
    custom_filters = Column(JSON, nullable=True)  # List of saved filter configurations
    custom_views = Column(JSON, nullable=True)  # List of saved view configurations
    
    # Notification preferences
    email_notifications_enabled = Column(String, default="true", nullable=False)  # "true", "false", "digest"
    push_notifications_enabled = Column(String, default="true", nullable=False)
    
    # Pomodoro session durations (in minutes)
    study_duration_minutes = Column(Integer, default=25, nullable=False)
    short_break_duration_minutes = Column(Integer, default=5, nullable=False)
    long_break_duration_minutes = Column(Integer, default=15, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

