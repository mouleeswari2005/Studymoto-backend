"""
Reminders REST endpoints.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Reminder, ReminderType
from app.services.reminder_service import ReminderService
from pydantic import BaseModel

router = APIRouter(prefix="/reminders", tags=["reminders"])


class ReminderResponse(BaseModel):
    """Reminder response schema."""
    id: int
    user_id: int
    task_id: Optional[int]
    exam_id: Optional[int]
    event_id: Optional[int]
    reminder_type: str
    reminder_time: datetime
    message: Optional[str]
    is_sent: bool
    channels: str
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReminderCreate(BaseModel):
    """Reminder creation schema."""
    task_id: Optional[int] = None
    exam_id: Optional[int] = None
    event_id: Optional[int] = None
    reminder_time: datetime
    message: Optional[str] = None
    channels: List[str] = ["in_app"]


@router.get("", response_model=List[ReminderResponse])
async def get_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_sent: Optional[bool] = None,
    reminder_type: Optional[ReminderType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's reminders."""
    query = select(Reminder).where(Reminder.user_id == current_user.id)
    
    if is_sent is not None:
        query = query.where(Reminder.is_sent == is_sent)
    if reminder_type:
        query = query.where(Reminder.reminder_type == reminder_type)
    
    query = query.order_by(Reminder.reminder_time.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    reminders = result.scalars().all()
    return reminders


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a manual reminder."""
    # Verify ownership
    if reminder_data.task_id:
        from app.models.task import Task
        result = await db.execute(
            select(Task).where(and_(Task.id == reminder_data.task_id, Task.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Task not found")
    
    if reminder_data.exam_id:
        from app.models.task import Exam
        result = await db.execute(
            select(Exam).where(and_(Exam.id == reminder_data.exam_id, Exam.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Exam not found")
    
    reminder = Reminder(
        user_id=current_user.id,
        task_id=reminder_data.task_id,
        exam_id=reminder_data.exam_id,
        event_id=reminder_data.event_id,
        reminder_type=ReminderType.TASK if reminder_data.task_id else ReminderType.EXAM if reminder_data.exam_id else ReminderType.EVENT,
        reminder_time=reminder_data.reminder_time,
        message=reminder_data.message,
        channels=",".join(reminder_data.channels),
        is_sent=False
    )
    
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    
    return reminder


@router.post("/check-overdue", response_model=List[ReminderResponse])
async def check_overdue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check and create reminders for overdue tasks."""
    reminders = await ReminderService.check_overdue_tasks(db, current_user.id)
    return reminders


@router.post("/check-near-due", response_model=List[ReminderResponse])
async def check_near_due(
    hours_ahead: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check and create reminders for tasks due soon."""
    reminders = await ReminderService.check_near_due_tasks(db, current_user.id, hours_ahead)
    return reminders


@router.get("/pending", response_model=List[ReminderResponse])
async def get_pending_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending reminders that need to be sent."""
    reminders = await ReminderService.get_pending_reminders(db, current_user.id)
    return reminders


@router.put("/{reminder_id}/mark-sent", response_model=ReminderResponse)
async def mark_reminder_sent(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a reminder as sent."""
    result = await db.execute(
        select(Reminder).where(
            and_(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        )
    )
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder = await ReminderService.mark_reminder_sent(db, reminder_id)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a reminder."""
    result = await db.execute(
        select(Reminder).where(
            and_(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        )
    )
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    await db.delete(reminder)
    await db.commit()
    
    return None

