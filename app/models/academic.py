"""
Academic calendar and scheduling models.
"""
from datetime import datetime, time
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class ScheduleType(str, Enum):
    """Schedule type enumeration."""
    WEEKLY = "weekly"  # Same schedule every week
    ROTATING = "rotating"  # Rotating schedule (e.g., A/B days)
    BLOCK = "block"  # Block schedule (longer periods, fewer classes per day)
    CUSTOM = "custom"  # Custom schedule


class Term(Base):
    """Academic term/semester model."""
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Fall 2024", "Spring Semester"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="terms")
    classes = relationship("Class", back_populates="term", cascade="all, delete-orphan")


class Class(Base):
    """Class/Subject model."""
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=True)
    name = Column(String, nullable=False)  # e.g., "Mathematics", "History"
    code = Column(String, nullable=True)  # e.g., "MATH101"
    color = Column(String, nullable=True)  # Hex color for UI
    instructor = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="classes")
    term = relationship("Term", back_populates="classes")
    schedule = relationship("Schedule", back_populates="class_obj", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("ClassSession", back_populates="class_obj", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="class_obj")
    exams = relationship("Exam", back_populates="class_obj")


class Schedule(Base):
    """Schedule model for a class."""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, unique=True)
    schedule_type = Column(String, nullable=False)  # ScheduleType enum
    timezone = Column(String, default="Asia/Kolkata", nullable=False)
    
    # For rotating schedules: pattern like ["A", "B"] or ["1", "2", "3", "4"]
    rotating_pattern = Column(JSON, nullable=True)
    
    # For custom schedules: full schedule definition
    custom_schedule = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    class_obj = relationship("Class", back_populates="schedule")
    sessions = relationship("ClassSession", back_populates="schedule", cascade="all, delete-orphan")


class ClassSession(Base):
    """Individual class session model."""
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    
    # Day of week (0=Monday, 6=Sunday) or specific date for custom schedules
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly/rotating
    specific_date = Column(DateTime, nullable=True)  # For custom schedules
    
    # For rotating schedules: which day in the pattern (e.g., "A" or "B")
    rotating_day = Column(String, nullable=True)
    
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    class_obj = relationship("Class", back_populates="sessions")
    schedule = relationship("Schedule", back_populates="sessions")

