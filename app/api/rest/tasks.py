"""
Tasks REST endpoints.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_premium
from app.core.timezone import now_ist, make_naive_ist
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.reminder_service import ReminderService
from app.services.streak_service import StreakService

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Use IST timezone utilities instead of local function
# make_naive_datetime is now make_naive_ist from app.core.timezone


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    class_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    due_before: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's tasks with filtering."""
    query = select(Task).where(Task.user_id == current_user.id)
    
    if class_id:
        query = query.where(Task.class_id == class_id)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if due_before:
        query = query.where(Task.due_date <= due_before)
    
    query = query.order_by(Task.due_date.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task."""
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    # Verify class belongs to user if provided
    if task_data.class_id:
        from app.models.academic import Class
        result = await db.execute(
            select(Class).where(and_(Class.id == task_data.class_id, Class.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Class not found")
    
    # Convert timezone-aware datetime to naive datetime in IST
    task_dict = task_data.model_dump()
    if task_dict.get("due_date"):
        task_dict["due_date"] = make_naive_ist(task_dict["due_date"])
    
    new_task = Task(
        **task_dict,
        user_id=current_user.id
    )
    
    # Set completed_at if task is created as completed
    if new_task.status == TaskStatus.COMPLETED and not new_task.completed_at:
        new_task.completed_at = make_naive_ist(now_ist())
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # Update streak if task was created as completed
    if new_task.status == TaskStatus.COMPLETED:
        await StreakService.check_and_update_streak(db, current_user.id)
    
    # Create smart reminders if task has due date
    if new_task.due_date:
        await ReminderService.create_smart_reminders_for_task(db, new_task)
    
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Track if status changed to completed (check BEFORE update)
    was_completed = task.status == TaskStatus.COMPLETED
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    # Convert timezone-aware datetime to naive datetime in IST
    if "due_date" in update_data and update_data["due_date"]:
        update_data["due_date"] = make_naive_ist(update_data["due_date"])
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Check if status is now completed (AFTER update)
    is_now_completed = task.status == TaskStatus.COMPLETED
    
    # Set completed_at timestamp if task was just completed
    if is_now_completed and not task.completed_at:
        task.completed_at = make_naive_ist(now_ist())
    elif not is_now_completed:
        task.completed_at = None

    task.updated_at = make_naive_ist(now_ist())
    
    await db.commit()
    await db.refresh(task)
    
    # Update streak if task was just completed (changed from not-completed to completed)
    if is_now_completed and not was_completed:
        await StreakService.check_and_update_streak(db, current_user.id)
    
    return task


@router.get("/stats", response_model=dict)
async def get_task_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task statistics (counts by status) for the current user."""
    # Count completed tasks
    completed_query = select(func.count(Task.id)).where(
        and_(
            Task.user_id == current_user.id,
            Task.status == TaskStatus.COMPLETED
        )
    )
    completed_result = await db.execute(completed_query)
    completed_count = completed_result.scalar() or 0
    
    # Count pending tasks (todo + in_progress)
    pending_query = select(func.count(Task.id)).where(
        and_(
            Task.user_id == current_user.id,
            or_(
                Task.status == TaskStatus.TODO,
                Task.status == TaskStatus.IN_PROGRESS
            )
        )
    )
    pending_result = await db.execute(pending_query)
    pending_count = pending_result.scalar() or 0
    
    # Count all tasks
    total_query = select(func.count(Task.id)).where(
        Task.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_count = total_result.scalar() or 0
    
    return {
        "completed": completed_count,
        "pending": pending_count,
        "total": total_count
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    # First verify the task exists and belongs to the user
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete the task using the correct async pattern
    await db.execute(
        delete(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    await db.commit()
    
    return None

