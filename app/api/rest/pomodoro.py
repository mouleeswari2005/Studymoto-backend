"""
Pomodoro timer REST endpoints.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.timezone import now_ist, make_naive_ist
from app.models.user import User
from app.models.focus import PomodoroSession, SessionType
from app.models.preference import UserPreference
from app.schemas.focus import PomodoroSessionCreate, PomodoroSessionResponse, FocusStatsResponse

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post("/start", response_model=PomodoroSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    session_data: PomodoroSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a Pomodoro session."""
    # Verify task belongs to user if provided
    if session_data.task_id:
        from app.models.task import Task
        result = await db.execute(
            select(Task).where(and_(Task.id == session_data.task_id, Task.user_id == current_user.id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Task not found")
    
    new_session = PomodoroSession(
        user_id=current_user.id,
        session_type=session_data.session_type,
        planned_duration_minutes=session_data.planned_duration_minutes,
        duration_minutes=0,  # Will be updated when session ends
        task_id=session_data.task_id,
        notes=session_data.notes,
        started_at=make_naive_ist(now_ist()),
        is_completed=False
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    return new_session


@router.get("/active", response_model=Optional[PomodoroSessionResponse])
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the currently active Pomodoro session for the user."""
    result = await db.execute(
        select(PomodoroSession).where(
            and_(
                PomodoroSession.user_id == current_user.id,
                PomodoroSession.is_completed == False
            )
        ).order_by(PomodoroSession.started_at.desc()).limit(1)
    )
    session = result.scalar_one_or_none()
    
    # Return None if no active session (frontend handles this)
    return session


@router.get("/{session_id}", response_model=PomodoroSessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific Pomodoro session by ID."""
    result = await db.execute(
        select(PomodoroSession).where(
            and_(
                PomodoroSession.id == session_id,
                PomodoroSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.put("/{session_id}/stop", response_model=PomodoroSessionResponse)
async def stop_session(
    session_id: int,
    duration_minutes: Optional[int] = Query(None, ge=0, description="Duration in minutes (optional, will calculate from start time if not provided)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop a Pomodoro session."""
    result = await db.execute(
        select(PomodoroSession).where(
            and_(
                PomodoroSession.id == session_id,
                PomodoroSession.user_id == current_user.id,
                PomodoroSession.is_completed == False
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already completed")
    
    # Validate that started_at exists (should always be set, but safety check)
    if not session.started_at:
        raise HTTPException(status_code=500, detail="Session missing start time")
    
    # Calculate exact duration from actual start time in decimal minutes (includes seconds)
    ended_at = make_naive_ist(now_ist())
    elapsed_time = ended_at - session.started_at
    elapsed_seconds = elapsed_time.total_seconds()
    
    # Use provided duration_minutes if given, otherwise calculate from timestamps
    if duration_minutes is not None:
        # Use provided value but ensure it's reasonable (not more than 2x the planned duration)
        max_reasonable = session.planned_duration_minutes * 2
        final_duration = float(min(duration_minutes, max_reasonable))
    else:
        # Calculate from actual elapsed time in decimal minutes (seconds / 60)
        # This preserves seconds precision (e.g., 90 seconds = 1.5 minutes)
        final_duration = elapsed_seconds / 60.0
    
    session.duration_minutes = final_duration
    session.ended_at = ended_at
    session.is_completed = True
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("", response_model=List[PomodoroSessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's Pomodoro sessions."""
    query = select(PomodoroSession).where(PomodoroSession.user_id == current_user.id)
    query = query.order_by(PomodoroSession.started_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions


@router.get("/stats", response_model=FocusStatsResponse)
async def get_focus_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get focus statistics for the user."""
    try:
        now = make_naive_ist(now_ist())
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get user's week start day preference
        try:
            pref_result = await db.execute(
                select(UserPreference).where(UserPreference.user_id == current_user.id)
            )
            preferences = pref_result.scalar_one_or_none()
            if preferences and preferences.week_start_day is not None:
                week_start_day = int(preferences.week_start_day)
                # Ensure week_start_day is in valid range (0-6)
                if week_start_day < 0 or week_start_day > 6:
                    week_start_day = 0
            else:
                week_start_day = 0  # Default to Monday (0)
        except Exception as e:
            # If there's an error accessing preferences, default to Monday
            week_start_day = 0
        
        # Calculate week start based on user preference
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        days_since_week_start = (current_weekday - week_start_day) % 7
        week_start = today_start - timedelta(days=days_since_week_start)
        
        # Today's stats
        today_query = select(
            func.sum(PomodoroSession.duration_minutes).label("total_minutes"),
            func.count(PomodoroSession.id).label("sessions")
        ).where(
            and_(
                PomodoroSession.user_id == current_user.id,
                PomodoroSession.is_completed == True,
                PomodoroSession.started_at >= today_start
            )
        )
        today_result = await db.execute(today_query)
        today_stats = today_result.first()
        
        # This week's stats
        week_query = select(
            func.sum(PomodoroSession.duration_minutes).label("total_minutes"),
            func.count(PomodoroSession.id).label("sessions")
        ).where(
            and_(
                PomodoroSession.user_id == current_user.id,
                PomodoroSession.is_completed == True,
                PomodoroSession.started_at >= week_start
            )
        )
        week_result = await db.execute(week_query)
        week_stats = week_result.first()
        
        # Average session duration (include all completed sessions for accurate average)
        avg_query = select(
            func.avg(PomodoroSession.duration_minutes).label("avg_duration")
        ).where(
            and_(
                PomodoroSession.user_id == current_user.id,
                PomodoroSession.is_completed == True
            )
        )
        avg_result = await db.execute(avg_query)
        avg_duration = avg_result.scalar() or 0.0
        
        # Safely extract values, handling None cases
        total_minutes_today = float(today_stats.total_minutes if today_stats and today_stats.total_minutes is not None else 0.0)
        sessions_today = int(today_stats.sessions if today_stats and today_stats.sessions is not None else 0)
        total_minutes_this_week = float(week_stats.total_minutes if week_stats and week_stats.total_minutes is not None else 0.0)
        sessions_this_week = int(week_stats.sessions if week_stats and week_stats.sessions is not None else 0)
        
        return FocusStatsResponse(
            total_minutes_today=total_minutes_today,
            total_minutes_this_week=total_minutes_this_week,
            sessions_today=sessions_today,
            sessions_this_week=sessions_this_week,
            average_session_duration=float(avg_duration)
        )
    except Exception as e:
        # Log the error and return default values
        import logging
        logging.error(f"Error getting focus stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/focus-view")
async def get_focus_view(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get minimalist focus view with only currently relevant tasks/sessions."""
    from app.models.task import Task, TaskStatus
    from datetime import datetime, timedelta
    
    # Get active tasks due in next 7 days
    seven_days = make_naive_ist(now_ist()) + timedelta(days=7)
    tasks_query = select(Task).where(
        and_(
            Task.user_id == current_user.id,
            Task.status != TaskStatus.COMPLETED,
            Task.due_date <= seven_days
        )
    ).order_by(Task.due_date.asc()).limit(5)
    
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    # Get upcoming exams in next 7 days
    from app.models.task import Exam
    exams_query = select(Exam).where(
        and_(
            Exam.user_id == current_user.id,
            Exam.exam_date <= seven_days
        )
    ).order_by(Exam.exam_date.asc()).limit(3)
    
    exams_result = await db.execute(exams_query)
    exams = exams_result.scalars().all()
    
    return {
        "tasks": [{"id": t.id, "title": t.title, "due_date": t.due_date} for t in tasks],
        "exams": [{"id": e.id, "title": e.title, "exam_date": e.exam_date} for e in exams]
    }

