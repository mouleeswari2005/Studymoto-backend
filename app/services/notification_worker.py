"""
Background worker for processing reminders and sending notifications.
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.services.reminder_service import ReminderService
from app.services.notification_service import NotificationService
from app.services.push_notification_service import PushNotificationService
from app.models.preference import UserPreference
from app.models.device import DeviceSubscription
from sqlalchemy import select
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationWorker:
    """Background worker for processing notifications."""
    
    def __init__(self):
        self.running = False
        self.task = None
    
    async def process_pending_reminders(self):
        """Process all pending reminders and send notifications."""
        async with AsyncSessionLocal() as db:
            try:
                # Get all pending reminders
                reminders = await ReminderService.get_pending_reminders(db)
                
                if not reminders:
                    logger.debug("No pending reminders to process")
                    return
                
                logger.info(f"Processing {len(reminders)} pending reminders")
                
                for reminder in reminders:
                    try:
                        await self._process_reminder(db, reminder)
                    except Exception as e:
                        logger.error(f"Error processing reminder {reminder.id}: {e}")
                        await db.rollback()
                        continue
                
            except Exception as e:
                logger.error(f"Error in process_pending_reminders: {e}")
                await db.rollback()
    
    async def _process_reminder(self, db: AsyncSession, reminder):
        """Process a single reminder."""
        # Get user preferences
        result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == reminder.user_id)
        )
        preferences = result.scalar_one_or_none()
        
        # Check if user has push notifications enabled
        push_enabled = False
        if preferences and preferences.push_notifications_enabled == "true":
            push_enabled = True
        
        # Create in-app notification
        notification = await NotificationService.create_notification_from_reminder(
            db, reminder
        )
        logger.info(f"Created notification {notification.id} from reminder {reminder.id}")
        
        # Send push notification if enabled and "push" is in channels
        if push_enabled and "push" in reminder.channels.split(","):
            # Get user's device subscriptions
            result = await db.execute(
                select(DeviceSubscription).where(
                    DeviceSubscription.user_id == reminder.user_id
                )
            )
            subscriptions = result.scalars().all()
            
            if subscriptions:
                # Send push to all user's devices
                for subscription in subscriptions:
                    success = PushNotificationService.send_push_notification(
                        subscription=subscription,
                        title=notification.title,
                        message=notification.message,
                        action_url=notification.action_url,
                        notification_type=notification.notification_type
                    )
                    if success:
                        logger.info(f"Push notification sent to device {subscription.id}")
                    else:
                        logger.warning(f"Failed to send push to device {subscription.id}")
            else:
                logger.debug(f"No device subscriptions found for user {reminder.user_id}")
        
        # Mark reminder as sent
        await ReminderService.mark_reminder_sent(db, reminder.id)
        logger.info(f"Reminder {reminder.id} marked as sent")
    
    async def start(self):
        """Start the background worker."""
        if self.running:
            logger.warning("Notification worker is already running")
            return
        
        self.running = True
        logger.info("Starting notification worker")
        
        async def worker_loop():
            while self.running:
                try:
                    await self.process_pending_reminders()
                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                
                # Wait before next check
                await asyncio.sleep(settings.NOTIFICATION_CHECK_INTERVAL)
        
        self.task = asyncio.create_task(worker_loop())
    
    async def stop(self):
        """Stop the background worker."""
        if not self.running:
            return
        
        logger.info("Stopping notification worker")
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass


# Global worker instance
notification_worker = NotificationWorker()

