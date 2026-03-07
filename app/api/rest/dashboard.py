"""
Dashboard REST endpoints.
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.timezone import now_ist, make_naive_ist
from app.models.user import User
from app.models.academic import Class, ClassSession
from app.models.task import Task, Exam, TaskStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data: upcoming classes, tasks, exams."""
    now = make_naive_ist(now_ist())
    today_end = now.replace(hour=23, minute=59, second=59)
    week_end = now + timedelta(days=7)
    
    # Get upcoming classes (today)
    # This is simplified - in production, you'd generate actual class sessions from schedules
    classes_query = select(Class).where(Class.user_id == current_user.id).limit(5)
    classes_result = await db.execute(classes_query)
    classes = classes_result.scalars().all()
    
    # Get upcoming tasks (next 7 days)
    tasks_query = select(Task).where(
        and_(
            Task.user_id == current_user.id,
            Task.status != TaskStatus.COMPLETED,
            Task.due_date <= week_end,
            Task.due_date >= now
        )
    ).order_by(Task.due_date.asc()).limit(10)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    # Get upcoming exams (next 7 days)
    exams_query = select(Exam).where(
        and_(
            Exam.user_id == current_user.id,
            Exam.exam_date <= week_end,
            Exam.exam_date >= now
        )
    ).order_by(Exam.exam_date.asc()).limit(10)
    exams_result = await db.execute(exams_query)
    exams = exams_result.scalars().all()
    
    # Get overdue tasks
    overdue_tasks_query = select(Task).where(
        and_(
            Task.user_id == current_user.id,
            Task.status != TaskStatus.COMPLETED,
            Task.due_date < now
        )
    ).order_by(Task.due_date.asc()).limit(5)
    overdue_result = await db.execute(overdue_tasks_query)
    overdue_tasks = overdue_result.scalars().all()
    
    return {
        "upcoming_classes": [
            {
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "color": c.color
            }
            for c in classes
        ],
        "upcoming_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "priority": t.priority.value,
                "status": t.status.value
            }
            for t in tasks
        ],
        "upcoming_exams": [
            {
                "id": e.id,
                "title": e.title,
                "exam_date": e.exam_date.isoformat(),
                "location": e.location
            }
            for e in exams
        ],
        "overdue_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "priority": t.priority.value
            }
            for t in overdue_tasks
        ]
    }

