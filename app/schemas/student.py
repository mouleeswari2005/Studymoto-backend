"""
Student-related schemas: Academic Projects, Extra Activities.
"""
from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, field_validator


class AcademicProjectBase(BaseModel):
    """Base academic project schema."""
    project_title: str
    no_of_project: int
    start_date: date
    submission_date: date
    completed_project: bool = False
    upload_area: Optional[str] = None


class AcademicProjectCreate(AcademicProjectBase):
    """Schema for academic project creation."""
    pass


class AcademicProjectUpdate(BaseModel):
    """Schema for academic project update."""
    project_title: Optional[str] = None
    no_of_project: Optional[int] = None
    start_date: Optional[date] = None
    submission_date: Optional[date] = None
    completed_project: Optional[bool] = None
    upload_area: Optional[str] = None


class AcademicProjectResponse(AcademicProjectBase):
    """Schema for academic project response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExtraActivityBase(BaseModel):
    """Base extra activity schema."""
    categories: str
    event_title: str
    winning_prizes: Optional[str] = None


class ExtraActivityCreate(ExtraActivityBase):
    """Schema for extra activity creation."""
    pass


class ExtraActivityUpdate(BaseModel):
    """Schema for extra activity update."""
    categories: Optional[str] = None
    event_title: Optional[str] = None
    winning_prizes: Optional[str] = None


class ExtraActivityResponse(ExtraActivityBase):
    """Schema for extra activity response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

