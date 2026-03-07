"""
Reminder service for smart reminder logic.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.core.timezone import now_ist, make_naive_ist
from app.models.notification import Reminder, ReminderType, NotificationChannel
from app.models.task import Task, TaskPriority, TaskStatus, Exam, Event


class ReminderService:
    """Service for managing reminders and notifications."""
    
    @staticmethod
    async def create_task_reminder(
        db: AsyncSession,
        task_id: int,
        user_id: int,
        reminder_time: datetime,
        channels: List[str] = None
    ) -> Reminder:
        """Create a reminder for a task."""
        if channels is None:
            channels = ["in_app"]
        
        reminder = Reminder(
            user_id=user_id,
            task_id=task_id,
            reminder_type=ReminderType.TASK,
            reminder_time=reminder_time,
            channels=",".join(channels),
            is_sent=False
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        return reminder
    
    @staticmethod
    async def create_exam_reminder(
        db: AsyncSession,
        exam_id: int,
        user_id: int,
        reminder_time: datetime,
        channels: List[str] = None
    ) -> Reminder:
        """Create a reminder for an exam."""
        if channels is None:
            channels = ["in_app"]
        
        reminder = Reminder(
            user_id=user_id,
            exam_id=exam_id,
            reminder_type=ReminderType.EXAM,
            reminder_time=reminder_time,
            channels=",".join(channels),
            is_sent=False
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        return reminder
    
    @staticmethod
    async def create_smart_reminders_for_task(
        db: AsyncSession,
        task: Task
    ) -> List[Reminder]:
        """Create smart reminders for a task based on priority and due date."""
        if not task.due_date:
            return []
        
        # Check user preferences for push notifications
        from app.models.preference import UserPreference
        from sqlalchemy import select
        result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == task.user_id)
        )
        preferences = result.scalar_one_or_none()
        
        # Build channels list
        channels = ["in_app", "email"]
        if preferences and preferences.push_notifications_enabled == "true":
            channels.append("push")
        
        reminders = []
        due_date = task.due_date
        now = make_naive_ist(now_ist())
        
        # Determine reminder times based on priority
        if task.priority == TaskPriority.URGENT:
            # Urgent: 1 day before, 6 hours before, 1 hour before
            reminder_times = [
                due_date - timedelta(days=1),
                due_date - timedelta(hours=6),
                due_date - timedelta(hours=1),
            ]
        elif task.priority == TaskPriority.HIGH:
            # High: 2 days before, 1 day before
            reminder_times = [
                due_date - timedelta(days=2),
                due_date - timedelta(days=1),
            ]
        elif task.priority == TaskPriority.MEDIUM:
            # Medium: 3 days before, 1 day before
            reminder_times = [
                due_date - timedelta(days=3),
                due_date - timedelta(days=1),
            ]
        else:
            # Low: 1 day before
            reminder_times = [
                due_date - timedelta(days=1),
            ]
        
        # Filter out past reminders
        reminder_times = [rt for rt in reminder_times if rt > now]
        
        # Create reminders
        for reminder_time in reminder_times:
            reminder = Reminder(
                user_id=task.user_id,
                task_id=task.id,
                reminder_type=ReminderType.TASK,
                reminder_time=reminder_time,
                channels=",".join(channels),
                is_sent=False,
                message=f"Task '{task.title}' is due soon"
            )
            reminders.append(reminder)
            db.add(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def create_smart_reminders_for_exam(
        db: AsyncSession,
        exam: Exam
    ) -> List[Reminder]:
        """Create smart reminders for an exam based on priority."""
        # Check user preferences for push notifications
        from app.models.preference import UserPreference
        from sqlalchemy import select
        result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == exam.user_id)
        )
        preferences = result.scalar_one_or_none()
        
        # Build channels list
        channels = ["in_app", "email"]
        if preferences and preferences.push_notifications_enabled == "true":
            channels.append("push")
        
        reminders = []
        exam_date = exam.exam_date
        now = make_naive_ist(now_ist())
        
        # Determine reminder times based on priority
        if exam.priority == TaskPriority.URGENT:
            # Urgent: 1 week before, 1 day before, 3 hours before
            reminder_times = [
                exam_date - timedelta(days=7),
                exam_date - timedelta(days=1),
                exam_date - timedelta(hours=3),
            ]
        elif exam.priority == TaskPriority.HIGH:
            # High: 1 week before, 2 days before
            reminder_times = [
                exam_date - timedelta(days=7),
                exam_date - timedelta(days=2),
            ]
        elif exam.priority == TaskPriority.MEDIUM:
            # Medium: 1 week before, 1 day before
            reminder_times = [
                exam_date - timedelta(days=7),
                exam_date - timedelta(days=1),
            ]
        else:
            # Low: 3 days before
            reminder_times = [
                exam_date - timedelta(days=3),
            ]
        
        # Filter out past reminders
        reminder_times = [rt for rt in reminder_times if rt > now]
        
        # Create reminders
        for reminder_time in reminder_times:
            reminder = Reminder(
                user_id=exam.user_id,
                exam_id=exam.id,
                reminder_type=ReminderType.EXAM,
                reminder_time=reminder_time,
                channels=",".join(channels),
                is_sent=False,
                message=f"Exam '{exam.title}' is coming up"
            )
            reminders.append(reminder)
            db.add(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def check_overdue_tasks(
        db: AsyncSession,
        user_id: int
    ) -> List[Reminder]:
        """Create reminders for overdue tasks."""
        now = make_naive_ist(now_ist())
        
        # Find overdue tasks
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.status != TaskStatus.COMPLETED,
                Task.due_date < now,
                Task.due_date.isnot(None)
            )
        )
        result = await db.execute(query)
        overdue_tasks = result.scalars().all()
        
        reminders = []
        for task in overdue_tasks:
            # Check if reminder already exists
            existing = await db.execute(
                select(Reminder).where(
                    and_(
                        Reminder.task_id == task.id,
                        Reminder.reminder_type == ReminderType.OVERDUE
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            # Check user preferences for push notifications
            from app.models.preference import UserPreference
            from sqlalchemy import select
            pref_result = await db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            preferences = pref_result.scalar_one_or_none()
            
            # Build channels list
            channels = ["in_app", "email"]
            if preferences and preferences.push_notifications_enabled == "true":
                channels.append("push")
            
            reminder = Reminder(
                user_id=user_id,
                task_id=task.id,
                reminder_type=ReminderType.OVERDUE,
                reminder_time=now,
                channels=",".join(channels),
                is_sent=False,
                message=f"Task '{task.title}' is overdue"
            )
            reminders.append(reminder)
            db.add(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def check_near_due_tasks(
        db: AsyncSession,
        user_id: int,
        hours_ahead: int = 24
    ) -> List[Reminder]:
        """Create reminders for tasks due soon."""
        now = make_naive_ist(now_ist())
        threshold = now + timedelta(hours=hours_ahead)
        
        # Find tasks due soon
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.status != TaskStatus.COMPLETED,
                Task.due_date >= now,
                Task.due_date <= threshold,
                Task.due_date.isnot(None)
            )
        )
        result = await db.execute(query)
        near_due_tasks = result.scalars().all()
        
        reminders = []
        for task in near_due_tasks:
            # Check if reminder already exists
            existing = await db.execute(
                select(Reminder).where(
                    and_(
                        Reminder.task_id == task.id,
                        Reminder.reminder_type == ReminderType.NEAR_DUE
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            # Check user preferences for push notifications
            from app.models.preference import UserPreference
            from sqlalchemy import select
            pref_result = await db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            preferences = pref_result.scalar_one_or_none()
            
            # Build channels list
            channels = ["in_app", "email"]
            if preferences and preferences.push_notifications_enabled == "true":
                channels.append("push")
            
            reminder = Reminder(
                user_id=user_id,
                task_id=task.id,
                reminder_type=ReminderType.NEAR_DUE,
                reminder_time=now,
                channels=",".join(channels),
                is_sent=False,
                message=f"Task '{task.title}' is due soon"
            )
            reminders.append(reminder)
            db.add(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def get_pending_reminders(
        db: AsyncSession,
        user_id: Optional[int] = None
    ) -> List[Reminder]:
        """Get reminders that need to be sent."""
        now = make_naive_ist(now_ist())
        query = select(Reminder).where(
            and_(
                Reminder.is_sent == False,
                Reminder.reminder_time <= now
            )
        )
        
        if user_id:
            query = query.where(Reminder.user_id == user_id)
        
        query = query.order_by(Reminder.reminder_time.asc())
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_reminder_sent(
        db: AsyncSession,
        reminder_id: int
    ) -> Reminder:
        """Mark a reminder as sent."""
        result = await db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()
        
        if reminder:
            reminder.is_sent = True
            reminder.sent_at = make_naive_ist(now_ist())
            await db.commit()
            await db.refresh(reminder)
        
        return reminder

