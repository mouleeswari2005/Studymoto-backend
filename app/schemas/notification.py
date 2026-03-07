"""
Notification schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Notification response schema."""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = None
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Notification creation schema."""
    title: str
    message: str
    notification_type: Optional[str] = None
    action_url: Optional[str] = None


class NotificationUpdate(BaseModel):
    """Notification update schema."""
    is_read: Optional[bool] = None




