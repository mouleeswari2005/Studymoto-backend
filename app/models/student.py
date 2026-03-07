"""
Student-related models: Academic Projects, Extra Activities.
"""
from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class AcademicProject(Base):
    """Academic Project model."""
    __tablename__ = "academic_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_title = Column(String, nullable=False)
    no_of_project = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    submission_date = Column(Date, nullable=False)
    completed_project = Column(Boolean, default=False, nullable=False)
    upload_area = Column(Text, nullable=True)  # Drive link
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="academic_projects")


class ExtraActivity(Base):
    """Extra Activity model."""
    __tablename__ = "extra_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    categories = Column(String, nullable=False)
    event_title = Column(String, nullable=False)
    winning_prizes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="extra_activities")

