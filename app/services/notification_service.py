"""
Notification service for managing in-app notifications.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.core.timezone import now_ist, make_naive_ist
from app.models.notification import Notification
from app.models.task import Task, Exam


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        title: str,
        message: str,
        notification_type: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            is_read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def create_notification_from_reminder(
        db: AsyncSession,
        reminder
    ) -> Notification:
        """Create a notification from a reminder."""
        # Build title and message from reminder
        title = f"Reminder: {reminder.reminder_type.replace('_', ' ').title()}"
        
        if reminder.message:
            message = reminder.message
        else:
            message = f"You have a {reminder.reminder_type.replace('_', ' ')} reminder"
        
        # Build action URL based on reminder type
        action_url = None
        if reminder.task_id:
            action_url = f"/tasks/{reminder.task_id}"
        elif reminder.exam_id:
            action_url = f"/exams/{reminder.exam_id}"
        
        notification = Notification(
            user_id=reminder.user_id,
            title=title,
            message=message,
            notification_type=reminder.reminder_type,
            action_url=action_url,
            is_read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def mark_notification_read(
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as read."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            notification.read_at = make_naive_ist(now_ist())
            await db.commit()
            await db.refresh(notification)
        
        return notification
    
    @staticmethod
    async def mark_notification_unread(
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as unread."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = False
            notification.read_at = None
            await db.commit()
            await db.refresh(notification)
        
        return notification
    
    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Delete a notification."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            await db.delete(notification)
            await db.commit()
            return True
        
        return False
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        is_read: Optional[bool] = None,
        notification_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """Get user's notifications with optional filters."""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        
        if notification_type:
            query = query.where(Notification.notification_type == notification_type)
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_all_read(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Mark all notifications as read for a user."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = make_naive_ist(now_ist())
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def delete_all_read(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Delete all read notifications for a user."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == True
                )
            )
        )
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            await db.delete(notification)
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Get count of unread notifications for a user."""
        from sqlalchemy import func
        result = await db.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        return result.scalar() or 0




