"""
Exams REST endpoints.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.timezone import now_ist, make_naive_ist
from app.models.user import User
from app.models.task import Exam, TaskPriority
from app.schemas.task import ExamCreate, ExamUpdate, ExamResponse
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/exams", tags=["exams"])


# Use IST timezone utilities instead of local function
# make_naive_datetime is now make_naive_ist from app.core.timezone


@router.get("", response_model=List[ExamResponse])
async def get_exams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    class_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
    before_date: Optional[datetime] = None,
    after_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's exams with filtering."""
    query = select(Exam).where(Exam.user_id == current_user.id)
    
    if class_id:
        query = query.where(Exam.class_id == class_id)
    if priority:
        query = query.where(Exam.priority == priority)
    if before_date:
        query = query.where(Exam.exam_date <= before_date)
    if after_date:
        query = query.where(Exam.exam_date >= after_date)
    
    query = query.order_by(Exam.exam_date.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    exams = result.scalars().all()
    return exams


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific exam."""
    result = await db.execute(
        select(Exam).where(and_(Exam.id == exam_id, Exam.user_id == current_user.id))
    )
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return exam


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    exam_data: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new exam."""
    # Verify class belongs to user if provided
    if exam_data.class_id:
        from app.models.academic import Class
        result = await db.execute(
            select(Class).where(and_(Class.id == exam_data.class_id, Class.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Class not found")

    # Convert timezone-aware datetime to naive datetime
    exam_dict = exam_data.model_dump()
    if exam_dict.get("exam_date"):
        exam_dict["exam_date"] = make_naive_ist(exam_dict["exam_date"])

    new_exam = Exam(
        **exam_dict,
        user_id=current_user.id
    )

    db.add(new_exam)
    await db.commit()
    await db.refresh(new_exam)

    # Create smart reminders for exam
    await ReminderService.create_smart_reminders_for_exam(db, new_exam)

    return new_exam


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an exam."""
    result = await db.execute(
        select(Exam).where(and_(Exam.id == exam_id, Exam.user_id == current_user.id))
    )
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Update fields
    update_data = exam_data.model_dump(exclude_unset=True)
    # Convert timezone-aware datetime to naive datetime
    if "exam_date" in update_data and update_data["exam_date"]:
        update_data["exam_date"] = make_naive_ist(update_data["exam_date"])
    
    for field, value in update_data.items():
        setattr(exam, field, value)
    
    exam.updated_at = make_naive_ist(now_ist())
    
    await db.commit()
    await db.refresh(exam)
    
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an exam."""
    result = await db.execute(
        select(Exam).where(and_(Exam.id == exam_id, Exam.user_id == current_user.id))
    )
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    await db.delete(exam)
    await db.commit()
    
    return None

