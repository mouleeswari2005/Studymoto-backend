"""
Academic schemas.
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel
from app.models.academic import ScheduleType


class TermBase(BaseModel):
    """Base term schema."""
    name: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True


class TermCreate(TermBase):
    """Schema for term creation."""
    pass


class TermUpdate(BaseModel):
    """Schema for term update."""
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class TermResponse(TermBase):
    """Schema for term response."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassBase(BaseModel):
    """Base class schema."""
    name: str
    code: Optional[str] = None
    color: Optional[str] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ClassCreate(ClassBase):
    """Schema for class creation."""
    term_id: Optional[int] = None


class ClassUpdate(BaseModel):
    """Schema for class update."""
    name: Optional[str] = None
    code: Optional[str] = None
    color: Optional[str] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    term_id: Optional[int] = None


class ClassResponse(ClassBase):
    """Schema for class response."""
    id: int
    user_id: int
    term_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassSessionBase(BaseModel):
    """Base class session schema."""
    day_of_week: Optional[int] = None
    specific_date: Optional[datetime] = None
    rotating_day: Optional[str] = None
    start_time: time
    end_time: time
    location: Optional[str] = None


class ClassSessionCreate(ClassSessionBase):
    """Schema for class session creation."""
    schedule_id: Optional[int] = None


class ClassSessionResponse(ClassSessionBase):
    """Schema for class session response."""
    id: int
    class_id: int
    schedule_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScheduleBase(BaseModel):
    """Base schedule schema."""
    schedule_type: ScheduleType
    timezone: str = "Asia/Kolkata"
    rotating_pattern: Optional[List[str]] = None
    custom_schedule: Optional[dict] = None


class ScheduleCreate(ScheduleBase):
    """Schema for schedule creation."""
    class_id: int


class ScheduleResponse(ScheduleBase):
    """Schema for schedule response."""
    id: int
    class_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

