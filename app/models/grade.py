"""
Grade tracking models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Grade(Base):
    """Grade model for assignments and exams."""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    
    assignment_name = Column(String, nullable=False)
    grade = Column(Float, nullable=False)  # Numeric grade
    max_grade = Column(Float, nullable=True)  # Maximum possible grade
    percentage = Column(Float, nullable=True)  # Calculated percentage
    letter_grade = Column(String, nullable=True)  # e.g., "A", "B+", "F"
    notes = Column(Text, nullable=True)
    graded_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="grades")
    class_obj = relationship("Class")
    exam = relationship("Exam", back_populates="grades")

