"""
Database models.
"""
from app.models.user import User
from app.models.academic import Term, Class, ClassSession, Schedule, ScheduleType
from app.models.task import Task, Exam, Project, Event, Subtask, TaskStatus, TaskPriority
from app.models.focus import PomodoroSession, SessionType
from app.models.preference import UserPreference
from app.models.grade import Grade
from app.models.content import BlogPost, FAQ, ContactMessage
from app.models.notification import Reminder, Notification
from app.models.device import DeviceSubscription
from app.models.student import AcademicProject, ExtraActivity
from app.models.planning import StudyPlan, SummerVacation, Note
from app.models.streak import Streak, StreakHistory

__all__ = [
    "User",
    "Term",
    "Class",
    "ClassSession",
    "Schedule",
    "ScheduleType",
    "Task",
    "Exam",
    "Project",
    "Event",
    "Subtask",
    "TaskStatus",
    "TaskPriority",
    "PomodoroSession",
    "SessionType",
    "UserPreference",
    "Grade",
    "BlogPost",
    "FAQ",
    "ContactMessage",
    "Reminder",
    "Notification",
    "DeviceSubscription",
    "AcademicProject",
    "ExtraActivity",
    "StudyPlan",
    "SummerVacation",
    "Note",
    "Streak",
    "StreakHistory",
]

