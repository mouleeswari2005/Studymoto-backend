"""
Task, exam, project schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    progress: int = 0


class TaskCreate(TaskBase):
    """Schema for task creation."""
    class_id: Optional[int] = None
    project_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Schema for task update."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    progress: Optional[int] = None
    class_id: Optional[int] = None
    project_id: Optional[int] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    user_id: int
    class_id: Optional[int]
    project_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SubtaskBase(BaseModel):
    """Base subtask schema."""
    title: str
    description: Optional[str] = None


class SubtaskCreate(SubtaskBase):
    """Schema for subtask creation."""
    task_id: int


class SubtaskResponse(SubtaskBase):
    """Schema for subtask response."""
    id: int
    task_id: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ExamBase(BaseModel):
    """Base exam schema."""
    title: str
    description: Optional[str] = None
    exam_date: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    syllabus_notes: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class ExamCreate(ExamBase):
    """Schema for exam creation."""
    class_id: Optional[int] = None


class ExamUpdate(BaseModel):
    """Schema for exam update."""
    title: Optional[str] = None
    description: Optional[str] = None
    exam_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    syllabus_notes: Optional[str] = None
    priority: Optional[TaskPriority] = None
    class_id: Optional[int] = None


class ExamResponse(ExamBase):
    """Schema for exam response."""
    id: int
    user_id: int
    class_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema."""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    progress: int = 0
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO


class ProjectCreate(ProjectBase):
    """Schema for project creation."""
    class_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """Schema for project update."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    progress: Optional[int] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    class_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    user_id: int
    class_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EventBase(BaseModel):
    """Base event schema."""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None


class EventCreate(EventBase):
    """Schema for event creation."""
    pass


class EventUpdate(BaseModel):
    """Schema for event update."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None


class EventResponse(EventBase):
    """Schema for event response."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

