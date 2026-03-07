"""
Reminder and notification models.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReminderType(str, Enum):
    """Reminder type enumeration."""
    TASK = "task"
    EXAM = "exam"
    EVENT = "event"
    STUDY_SESSION = "study_session"
    OVERDUE = "overdue"
    NEAR_DUE = "near_due"


class NotificationChannel(str, Enum):
    """Notification channel enumeration."""
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class Reminder(Base):
    """Reminder model."""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    reminder_type = Column(SQLEnum(ReminderType), nullable=False)
    reminder_time = Column(DateTime, nullable=False)
    message = Column(Text, nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    channels = Column(String, nullable=False)  # Comma-separated: "email,push"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    task = relationship("Task", back_populates="reminders")
    exam = relationship("Exam", back_populates="reminders")
    event = relationship("Event", back_populates="reminders")


class Notification(Base):
    """Notification model (for in-app notifications)."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=True)  # e.g., "reminder", "grade", "system"
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(String, nullable=True)  # URL to navigate to when clicked
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

