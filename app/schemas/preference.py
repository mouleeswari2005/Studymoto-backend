"""
User preferences schemas.
"""
from typing import Optional, Dict, List
from pydantic import BaseModel


class UserPreferenceBase(BaseModel):
    """Base user preference schema."""
    theme_color: Optional[str] = None
    banner_image_url: Optional[str] = None
    default_calendar_view: str = "week"
    time_format: str = "12h"
    timezone: str = "Asia/Kolkata"
    week_start_day: int = 0
    custom_filters: Optional[List[Dict]] = None
    custom_views: Optional[List[Dict]] = None
    email_notifications_enabled: str = "true"
    push_notifications_enabled: str = "true"
    study_duration_minutes: int = 25
    short_break_duration_minutes: int = 5
    long_break_duration_minutes: int = 15


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for preference creation."""
    pass


class UserPreferenceUpdate(BaseModel):
    """Schema for preference update."""
    theme_color: Optional[str] = None
    banner_image_url: Optional[str] = None
    default_calendar_view: Optional[str] = None
    time_format: Optional[str] = None
    timezone: Optional[str] = None
    week_start_day: Optional[int] = None
    custom_filters: Optional[List[Dict]] = None
    custom_views: Optional[List[Dict]] = None
    email_notifications_enabled: Optional[str] = None
    push_notifications_enabled: Optional[str] = None
    study_duration_minutes: Optional[int] = None
    short_break_duration_minutes: Optional[int] = None
    long_break_duration_minutes: Optional[int] = None


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for preference response."""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

