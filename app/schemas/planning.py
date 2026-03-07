"""
Study Plan, Summer Vacation, and Notes schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudyPlanBase(BaseModel):
    """Base study plan schema."""
    title: str
    description: Optional[str] = None
    plan_content: Optional[str] = None


class StudyPlanCreate(StudyPlanBase):
    """Schema for study plan creation."""
    pass


class StudyPlanUpdate(BaseModel):
    """Schema for study plan update."""
    title: Optional[str] = None
    description: Optional[str] = None
    plan_content: Optional[str] = None


class StudyPlanResponse(StudyPlanBase):
    """Schema for study plan response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SummerVacationBase(BaseModel):
    """Base summer vacation schema."""
    date: str
    time: str
    vacation_plan: Optional[str] = None
    trip_plan: Optional[str] = None


class SummerVacationCreate(SummerVacationBase):
    """Schema for summer vacation creation."""
    pass


class SummerVacationUpdate(BaseModel):
    """Schema for summer vacation update."""
    date: Optional[str] = None
    time: Optional[str] = None
    vacation_plan: Optional[str] = None
    trip_plan: Optional[str] = None


class SummerVacationResponse(SummerVacationBase):
    """Schema for summer vacation response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    """Base note schema."""
    date: str
    time: str
    notes: Optional[str] = None


class NoteCreate(NoteBase):
    """Schema for note creation."""
    pass


class NoteUpdate(BaseModel):
    """Schema for note update."""
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None


class NoteResponse(NoteBase):
    """Schema for note response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True




