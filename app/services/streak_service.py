"""
Streak service for tracking daily task completion streaks.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.core.timezone import now_ist, get_today_ist_date, get_start_of_day_ist, get_end_of_day_ist, make_naive_ist
from app.models.streak import Streak, StreakHistory
from app.models.task import Task, TaskStatus


class StreakService:
    """Service for managing streaks and streak history."""
    
    @staticmethod
    async def get_or_create_streak(
        db: AsyncSession,
        user_id: int
    ) -> Streak:
        """Get or create a streak record for a user."""
        result = await db.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()
        
        if not streak:
            streak = Streak(
                user_id=user_id,
                current_streak=0,
                last_completion_date=None
            )
            db.add(streak)
            await db.commit()
            await db.refresh(streak)
        
        return streak
    
    @staticmethod
    async def check_daily_completion(
        db: AsyncSession,
        user_id: int,
        target_date: Optional[date] = None
    ) -> bool:
        """Check if user completed at least one task on the given date (defaults to today in IST)."""
        if target_date is None:
            target_date = get_today_ist_date()

        # Check if any task was completed on this date in IST timezone
        start_of_day = make_naive_ist(get_start_of_day_ist(target_date))
        end_of_day = make_naive_ist(get_end_of_day_ist(target_date))
        
        # Query for tasks that are completed and have completed_at within the target date
        # Also handle edge case where status is COMPLETED but completed_at might be None
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at.isnot(None),
                Task.completed_at >= start_of_day,
                Task.completed_at <= end_of_day
            )
        )
        result = await db.execute(query)
        completed_tasks = result.scalars().all()
        
        return len(completed_tasks) > 0
    
    @staticmethod
    async def check_and_update_streak(
        db: AsyncSession,
        user_id: int
    ) -> Streak:
        """Check if user completed a task today (IST) and update streak accordingly."""
        today = get_today_ist_date()
        streak = await StreakService.get_or_create_streak(db, user_id)
        
        # Check if user already completed a task today
        already_completed_today = await StreakService.check_daily_completion(
            db, user_id, today
        )
        
        if not already_completed_today:
            # No task completed today, no change to streak
            return streak
        
        # User completed a task today
        # Check if this is the first completion today (to avoid multiple updates)
        if streak.last_completion_date == today:
            # Already updated today, no change needed
            return streak
        
        # Update streak based on last completion date
        if streak.last_completion_date is None:
            # First time completing a task
            streak.current_streak = 1
        elif streak.last_completion_date == today - timedelta(days=1):
            # Consecutive day - increment streak
            streak.current_streak += 1
        else:
            # Gap detected - reset to 1 (starting a new streak)
            streak.current_streak = 1
        
        streak.last_completion_date = today
        streak.updated_at = make_naive_ist(now_ist())
        
        await db.commit()
        await db.refresh(streak)
        
        # Update streak history
        await StreakService.update_streak_history(db, user_id, today, True, streak.current_streak)
        
        return streak
    
    @staticmethod
    async def update_streak_history(
        db: AsyncSession,
        user_id: int,
        target_date: date,
        completed: bool,
        streak_count: int
    ) -> StreakHistory:
        """Update or create streak history entry for a specific date."""
        # Check if history entry already exists for this date
        result = await db.execute(
            select(StreakHistory).where(
                and_(
                    StreakHistory.user_id == user_id,
                    StreakHistory.date == target_date
                )
            )
        )
        history_entry = result.scalar_one_or_none()
        
        if history_entry:
            # Update existing entry
            history_entry.completed = completed
            history_entry.streak_count = streak_count
        else:
            # Create new entry
            history_entry = StreakHistory(
                user_id=user_id,
                date=target_date,
                completed=completed,
                streak_count=streak_count
            )
            db.add(history_entry)
        
        await db.commit()
        await db.refresh(history_entry)
        return history_entry
    
    @staticmethod
    async def get_streak_history(
        db: AsyncSession,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[StreakHistory]:
        """Get streak history for a user within a date range."""
        query = select(StreakHistory).where(StreakHistory.user_id == user_id)
        
        if start_date:
            query = query.where(StreakHistory.date >= start_date)
        if end_date:
            query = query.where(StreakHistory.date <= end_date)
        
        query = query.order_by(StreakHistory.date.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_current_streak(
        db: AsyncSession,
        user_id: int
    ) -> Streak:
        """Get current streak information for a user."""
        streak = await StreakService.get_or_create_streak(db, user_id)
        
        # Check if streak is still active (completed a task today in IST)
        today = get_today_ist_date()
        if streak.last_completion_date != today:
            # Streak might be broken, but we don't auto-reset until next completion attempt
            # The streak count remains but is considered inactive
            pass
        
        return streak
    
    @staticmethod
    async def get_best_streak(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Get the best (highest) streak count from history."""
        query = select(func.max(StreakHistory.streak_count)).where(
            StreakHistory.user_id == user_id
        )
        result = await db.execute(query)
        best_streak = result.scalar_one_or_none()
        
        # Also check current streak
        current_streak = await StreakService.get_current_streak(db, user_id)
        
        if best_streak is None:
            return current_streak.current_streak
        
        return max(best_streak, current_streak.current_streak)

